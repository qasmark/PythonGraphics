import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QComboBox, QToolButton, QHBoxLayout
from PyQt5.QtOpenGL import QGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *
import random


class Dice3DWidget(QGLWidget):
    def __init__(self, parent=None):
        super(Dice3DWidget, self).__init__(parent)
        self.dice_type = 'D6'
        self.dice_count = 1
        self.dice_positions = []
        self.reset_dice_positions()

        self.angle_x, self.angle_y = 25, 30
        self.light_position = [1.0, 4.0, 1.0, 1.0]

    def reset_dice_positions(self):
        self.dice_positions = [(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)) for _ in range(self.dice_count)]
        self.update()

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        glLightfv(GL_LIGHT0, GL_POSITION, self.light_position)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])

        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 50)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / h, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -5.0)

        glRotatef(self.angle_x, 1.0, 0.0, 0.0)
        glRotatef(self.angle_y, 0.0, 1.0, 0.0)

        for position in self.dice_positions:
            self.draw_dice(position)

        glFlush()

    def draw_dice(self, position):
        glPushMatrix()
        glTranslatef(*position)
        
        if self.dice_type == 'D4':
            self.draw_d4()
        elif self.dice_type == 'D6':
            self.draw_d6()
        elif self.dice_type == 'D8':
            self.draw_d8()
        elif self.dice_type == 'D10':
            self.draw_d10()
        elif self.dice_type == 'D12':
            self.draw_d12()
        elif self.dice_type == 'D20':
            self.draw_d20()
        elif self.dice_type == 'D100':
            self.draw_d10()

        glPopMatrix()

    def draw_d4(self):
        glBegin(GL_TRIANGLES)
        vertices = [
            [1, 1, 1],
            [1, -1, -1],
            [-1, 1, -1],
            [-1, -1, 1]
        ]
        indices = [(0, 1, 2), (1, 2, 3), (0, 1, 3), (0, 2, 3)]
        for i, color in enumerate([(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0)]):
            glColor3f(*color)
            for vertex in indices[i]:
                glVertex3fv(vertices[vertex])
        glEnd()

    def draw_d6(self):
        glBegin(GL_QUADS)
        vertices = [
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
        ]
        faces = [
            (0, 1, 2, 3),
            (4, 5, 6, 7),
            (0, 3, 7, 4),
            (1, 5, 6, 2),
            (3, 2, 6, 7),
            (0, 1, 5, 4)
        ]

        colors = [
            (1, 0, 0), (0, 1, 0), (0, 0, 1),
            (1, 1, 0), (1, 0, 1), (0, 1, 1)
        ]

        for i, face in enumerate(faces):
            glColor3f(*colors[i % len(colors)])
            for vertex in face:
                glVertex3fv(vertices[vertex])
    
        glEnd()

    def draw_d8(self):
        vertices = [
            [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]
        ]
        faces = [
            (0, 2, 4), (0, 4, 3), (0, 3, 1), (0, 1, 2),
            (1, 3, 5), (1, 5, 2), (2, 5, 4), (3, 4, 5)
        ]
        colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), 
                  (1, 0, 1), (0, 1, 1), (0.5, 0.5, 0.5), (1, 0.5, 0)]
    
        for i, face in enumerate(faces):
            glColor3f(*colors[i % len(colors)])
            glBegin(GL_TRIANGLES)
            for vertex in face:
                glVertex3fv(vertices[vertex])
            glEnd()

        glColor3f(1, 1, 1)
        for idx, vertex in enumerate(vertices):
            glPushMatrix()
            glTranslatef(*vertex)
            self.render_text(str(idx + 1))
            glPopMatrix()

    def draw_d10(self):
        vertices = [
            [0, 0, 1], [0.5, 0, 0.5], [1, 0, 0], [0.5, 0, -0.5],
            [0, 0, -1], [-0.5, 0, -0.5], [-1, 0, 0], [-0.5, 0, 0.5],
            [0, 0, 1], [0, 0, -1]
        ]
        faces = [
            (0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 5), 
            (0, 5, 6), (0, 6, 7), (0, 7, 1), (2, 1, 8),
            (3, 2, 8), (4, 3, 8), (5, 4, 8), (6, 5, 8), 
            (7, 6, 8)
        ]
        colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), 
                  (1, 0, 1), (0, 1, 1), (0.5, 0.5, 0.5), (1, 0.5, 0)]
    
        for i, face in enumerate(faces):
            glColor3f(*colors[i % len(colors)])
            glBegin(GL_TRIANGLES)
            for vertex in face:
                glVertex3fv(vertices[vertex])
            glEnd()

        glColor3f(1, 1, 1)
        for idx, vertex in enumerate(vertices):
            glPushMatrix()
            glTranslatef(*vertex)
            self.render_text(str((idx % 10) + 1))
            glPopMatrix()

        glColor3f(1, 1, 1)
        for idx, vertex in enumerate(vertices):
            glPushMatrix()
            glTranslatef(*vertex)
            self.render_text(str((idx % 10) + 1))
            glPopMatrix()

    def draw_d12(self):
        phi = (1 + np.sqrt(5)) / 2
        vertices = [
            [1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1],
            [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1],
            [0, 1 / phi, phi], [0, 1 / phi, -phi], 
            [0, -1 / phi, phi], [0, -1 / phi, -phi],
            [phi, 0, 1 / phi], [-phi, 0, 1 / phi], 
            [phi, 0, -1 / phi], [-phi, 0, -1 / phi]
        ]
        faces = [
            (0, 8, 4, 12, 10), (0, 10, 2, 14, 8),
            (0, 12, 6, 2, 10), (1, 11, 9, 5, 13),
            (1, 13, 3, 15, 11), (1, 5, 7, 3, 13),
            (3, 7, 9, 11, 15), (2, 10, 0, 8, 14),
            (2, 14, 12, 4, 8), (5, 7, 3, 9, 11),
            (4, 6, 2, 0, 10), (6, 12, 8, 14, 2)
        ]
        colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), 
                  (1, 0, 1), (0, 1, 1), (0.5, 0.5, 0.5), (1, 0.5, 0)]
    
        for i, face in enumerate(faces):
            glColor3f(*colors[i % len(colors)])
            glBegin(GL_POLYGON)
            for vertex in face:
                glVertex3fv(vertices[vertex])
            glEnd()

        glColor3f(1, 1, 1)
        for idx, vertex in enumerate(vertices):
            glPushMatrix()
            glTranslatef(*vertex)
            self.render_text(str(idx + 1))
            glPopMatrix()


    def draw_d20(self):
        t = (1.0 + np.sqrt(5.0)) / 2.0
        vertices = [
            [-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0],
            [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t],
            [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1]
        ]
        faces = [
            (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
            (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
            (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
            (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)
        ]
        colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), 
                  (1, 0, 1), (0, 1, 1), (0.5, 0.5, 0.5), (1, 0.5, 0)]
    
        for i, face in enumerate(faces):
            glColor3f(*colors[i % len(colors)])
            glBegin(GL_TRIANGLES)
            for vertex in face:
                glVertex3fv(vertices[vertex])
            glEnd()

        glColor3f(1, 1, 1)
        for idx, vertex in enumerate(vertices):
            glPushMatrix()
            glTranslatef(*vertex)
            self.render_text(str(idx + 1))
            glPopMatrix()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("3D Dice Roller")
        self.setGeometry(100, 100, 800, 600)

        self.dice_widget = Dice3DWidget(self)

        self.dice_type_combo = QComboBox(self)
        self.dice_type_combo.addItems(['D4', 'D6', 'D8', 'D10', 'D12', 'D20', 'D100'])
        self.dice_type_combo.currentTextChanged.connect(self.change_dice_type)

        self.roll_button = QToolButton(self)
        self.roll_button.setText("🎲")
        self.roll_button.setToolTip("Roll Dice")
        self.roll_button.clicked.connect(self.roll_dice)

        self.add_dice_button = QToolButton(self)
        self.add_dice_button.setText("➕")
        self.add_dice_button.setToolTip("Add Dice")
        self.add_dice_button.clicked.connect(self.add_dice)

        self.remove_dice_button = QToolButton(self)
        self.remove_dice_button.setText("➖")
        self.remove_dice_button.setToolTip("Remove Dice")
        self.remove_dice_button.clicked.connect(self.remove_dice)

        # Horizontal layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.roll_button)
        button_layout.addWidget(self.add_dice_button)
        button_layout.addWidget(self.remove_dice_button)

        layout = QVBoxLayout()
        layout.addWidget(self.dice_type_combo)
        layout.addLayout(button_layout)
        layout.addWidget(self.dice_widget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def change_dice_type(self, dice_type):
        self.dice_widget.dice_type = dice_type
        self.dice_widget.update()

    def roll_dice(self):
        self.dice_widget.reset_dice_positions()

    def add_dice(self):
        self.dice_widget.dice_count += 1
        self.dice_widget.reset_dice_positions()

    def remove_dice(self):
        if self.dice_widget.dice_count > 1:
            self.dice_widget.dice_count -= 1
            self.dice_widget.reset_dice_positions()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())