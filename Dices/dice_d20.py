import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QOpenGLWidget,
                             QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QGroupBox)
from PyQt5.QtCore import Qt, QTimer, QPoint, QSize
from PyQt5.QtGui import QSurfaceFormat, QVector3D
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
from math import cos, sin, radians, sqrt


class Dice(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('D&D Dice Roller 3D')
        self.setGeometry(100, 100, 1200, 800)

        # Основные layout
        main_layout = QHBoxLayout()
        control_panel = QVBoxLayout()

        # Виджет OpenGL
        self.glWidget = DiceGLWidget(self)
        main_layout.addWidget(self.glWidget, 4)

        # Панель управления
        control_group = QGroupBox("Dice Controls")
        self.result_label = QLabel("Result: ")

        # Кнопки для бросков
        self.d4_btn = QPushButton("Roll D4")
        self.d6_btn = QPushButton("Roll D6")
        self.d8_btn = QPushButton("Roll D8")
        self.d10_btn = QPushButton("Roll D10")
        self.d12_btn = QPushButton("Roll D12")
        self.d20_btn = QPushButton("Roll D20")
        self.d100_btn = QPushButton("Roll D100")

        # Стили кнопок
        btn_style = "QPushButton {padding: 10px; font-size: 14px;}"
        self.d4_btn.setStyleSheet(btn_style + "background: #FF6666;")
        self.d6_btn.setStyleSheet(btn_style + "background: #6688FF;")
        self.d8_btn.setStyleSheet(btn_style + "background: #66FF66;")
        self.d10_btn.setStyleSheet(btn_style + "background: #FF66FF;")
        self.d12_btn.setStyleSheet(btn_style + "background: #FFFF66;")
        self.d20_btn.setStyleSheet(btn_style + "background: #66FFFF;")
        self.d100_btn.setStyleSheet(btn_style + "background: #AAAAAA;")

        # Привязка обработчиков
        self.d4_btn.clicked.connect(lambda: self.glWidget.roll_dice('D4'))
        self.d6_btn.clicked.connect(lambda: self.glWidget.roll_dice('D6'))
        self.d8_btn.clicked.connect(lambda: self.glWidget.roll_dice('D8'))
        self.d10_btn.clicked.connect(lambda: self.glWidget.roll_dice('D10'))
        self.d12_btn.clicked.connect(lambda: self.glWidget.roll_dice('D12'))
        self.d20_btn.clicked.connect(lambda: self.glWidget.roll_dice('D20'))
        self.d100_btn.clicked.connect(lambda: self.glWidget.roll_dice('D100'))

        # Компоновка
        control_panel.addWidget(self.result_label)
        control_panel.addWidget(self.d4_btn)
        control_panel.addWidget(self.d6_btn)
        control_panel.addWidget(self.d8_btn)
        control_panel.addWidget(self.d10_btn)
        control_panel.addWidget(self.d12_btn)
        control_panel.addWidget(self.d20_btn)
        control_panel.addWidget(self.d100_btn)
        control_panel.addStretch()
        control_group.setLayout(control_panel)

        main_layout.addLayout(control_panel, 1)
        self.setLayout(main_layout)


class DiceGLWidget(QOpenGLWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.dice_objects = []
        self.rotation = [30, 45, 0]  # Изометрический вид
        self.light_pos = [5, 10, 5]
        self.animating = False
        self.current_die = None

        # Настройки таймера анимации
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.dice_types = {
            'D4': {'faces': 4, 'color': [1.0, 0.4, 0.4, 1.0]},
            'D6': {'faces': 6, 'color': [0.4, 0.4, 1.0, 1.0]},
            'D8': {'faces': 8, 'color': [0.4, 1.0, 0.4, 1.0]},
            'D10': {'faces': 10, 'color': [1.0, 0.4, 1.0, 1.0]},
            'D12': {'faces': 12, 'color': [1.0, 1.0, 0.4, 1.0]},
            'D20': {'faces': 20, 'color': [0.4, 1.0, 1.0, 1.0]},
            'D100': {'faces': 10, 'color': [0.8, 0.8, 0.8, 1.0]}
        }

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        glLightfv(GL_LIGHT0, GL_POSITION, self.light_pos)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])

        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialfv(GL_FRONT, GL_SHININESS, 100)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h, 1, 100)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(0, 8, 8, 0, 0, 0, 0, 1, 0)

        # Отрисовка всех кубиков
        for die in self.dice_objects:
            glPushMatrix()
            glTranslatef(*die['position'])
            glRotatef(die['rotation'][0], 1, 0, 0)
            glRotatef(die['rotation'][1], 0, 1, 0)
            glRotatef(die['rotation'][2], 0, 0, 1)
            glColor4fv(die['color'])
            self.draw_die(die)
            glPopMatrix()

    def draw_die(self, die):
        vertices = die['vertices']
        glBegin(GL_TRIANGLES)
        for face in vertices:
            for vertex in face:
                glVertex3fv(vertex)
        glEnd()

    def roll_dice(self, dice_type):
        if self.animating: return

        # Создаем новый кубик
        new_die = {
            'type': dice_type,
            'vertices': self.generate_dice(dice_type),
            'position': [random.uniform(-2, 2), 5, random.uniform(-2, 2)],
            'rotation': [0, 0, 0],
            'velocity': [random.uniform(-0.1, 0.1), -0.5, random.uniform(-0.1, 0.1)],
            'angular_velocity': [random.uniform(-5, 5), random.uniform(-5, 5), random.uniform(-5, 5)],
            'color': self.dice_types[dice_type]['color'],
            'stopped': False
        }

        if dice_type == 'D100':
            # Добавляем второй D10 для D100
            self.dice_objects.append(new_die)
            new_die2 = new_die.copy()
            new_die2['position'][0] += 1.5
            self.dice_objects.append(new_die2)
        else:
            self.dice_objects.append(new_die)

        self.animating = True
        self.timer.start(16)

    def animate(self):
        all_stopped = True
        for die in self.dice_objects:
            if die['stopped']: continue

            # Обновление физики
            die['position'][1] += die['velocity'][1]
            die['rotation'][0] += die['angular_velocity'][0]
            die['rotation'][1] += die['angular_velocity'][1]
            die['rotation'][2] += die['angular_velocity'][2]

            # Проверка столкновения с "полом"
            if die['position'][1] < 0:
                die['position'][1] = 0
                die['velocity'][1] *= -0.5
                die['angular_velocity'] = [av * 0.8 for av in die['angular_velocity']]

                if abs(die['velocity'][1]) < 0.01 and all(abs(av) < 0.1 for av in die['angular_velocity']):
                    die['stopped'] = True
                    result = self.calculate_result(die)
                    self.parent().result_label.setText(f"Result: {result}")
                else:
                    all_stopped = False
            else:
                die['velocity'][1] -= 0.1  # Гравитация
                all_stopped = False

        if all_stopped:
            self.timer.stop()
            self.animating = False

        self.update()

    def calculate_result(self, die):
        # Определяем верхнюю грань
        up_vector = QVector3D(0, 1, 0)
        max_dot = -1
        result = 1

        for i, face in enumerate(die['vertices']):
            # Вычисляем нормаль грани
            v1 = np.array(face[0])
            v2 = np.array(face[1])
            v3 = np.array(face[2])

            normal = np.cross(v2 - v1, v3 - v1)
            normal = normal / np.linalg.norm(normal)

            # Преобразуем нормаль с учетом вращения
            rotation_matrix = self.get_rotation_matrix(die['rotation'])
            rotated_normal = np.dot(rotation_matrix, normal)

            dot_product = np.dot(rotated_normal, [0, 1, 0])
            if dot_product > max_dot:
                max_dot = dot_product
                result = i + 1

        return result % die['vertices'].__len__() or die['vertices'].__len__()

    def get_rotation_matrix(self, rotation):
        rx = np.radians(rotation[0])
        ry = np.radians(rotation[1])
        rz = np.radians(rotation[2])

        Rx = np.array([[1, 0, 0],
                       [0, cos(rx), -sin(rx)],
                       [0, sin(rx), cos(rx)]])

        Ry = np.array([[cos(ry), 0, sin(ry)],
                       [0, 1, 0],
                       [-sin(ry), 0, cos(ry)]])

        Rz = np.array([[cos(rz), -sin(rz), 0],
                       [sin(rz), cos(rz), 0],
                       [0, 0, 1]])

        return Rz @ Ry @ Rx

    def generate_dice(self, dice_type):
        if dice_type == 'D4':
            return self.create_d4()
        elif dice_type == 'D6':
            return self.create_d6()
        elif dice_type == 'D8':
            return self.create_d8()
        elif dice_type == 'D10':
            return self.create_d10()
        elif dice_type == 'D12':
            return self.create_d12()
        elif dice_type == 'D20':
            return self.create_d20()
        elif dice_type == 'D100':
            return self.create_d10()

    def create_d4(self):
        vertices = []
        v = [(0, 1, 0), (1, 0, 0), (-1, 0, 0), (0, 0, 1)]
        faces = [[v[0], v[1], v[2]],
                 [v[0], v[1], v[3]],
                 [v[0], v[2], v[3]],
                 [v[1], v[2], v[3]]]
        return faces

    def create_d6(self):
        vertices = []
        s = 0.8
        faces = [
            [[-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s]],
            [[-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s]],
            [[-s, -s, -s], [-s, s, -s], [-s, s, s], [-s, -s, s]],
            [[s, -s, -s], [s, s, -s], [s, s, s], [s, -s, s]],
            [[-s, -s, -s], [s, -s, -s], [s, -s, s], [-s, -s, s]],
            [[-s, s, -s], [s, s, -s], [s, s, s], [-s, s, s]]
        ]
        return [self.triangulate_quad(face) for face in faces]

    def triangulate_quad(self, quad):
        return [quad[0], quad[1], quad[2], quad[0], quad[2], quad[3]]

    # Реализации для других кубиков аналогичны (D8, D10 и т.д.)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Dice()
    window.show()
    sys.exit(app.exec_())