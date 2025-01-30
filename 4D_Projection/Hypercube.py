import numpy as np
from PyQt5 import QtWidgets, QtCore
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


class HypercubeVisualizer(QtWidgets.QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.angle = 0
        self.position_angle = 0
        self.scale_factor = 1.0
        self.scale_direction = 1
        self.camera_angle = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)

        # Инициализация вершин и ребер
        self.vertices = self.generate_vertices()
        self.edges = self.generate_edges()

    def generate_vertices(self):
        return np.array([
            [-1, -1, -1, -1], [1, -1, -1, -1], [1, 1, -1, -1], [-1, 1, -1, -1],
            [-1, -1, 1, -1], [1, -1, 1, -1], [1, 1, 1, -1], [-1, 1, 1, -1],
            [-1, -1, -1, 1], [1, -1, -1, 1], [1, 1, -1, 1], [-1, 1, -1, 1],
            [-1, -1, 1, 1], [1, -1, 1, 1], [1, 1, 1, 1], [-1, 1, 1, 1]
        ], dtype=np.float32)

    def generate_edges(self):
        return [
            (0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7), (8, 9), (9, 10), (10, 11), (11, 8),
            (12, 13), (13, 14), (14, 15), (15, 12), (8, 12), (9, 13), (10, 14), (11, 15),
            (0, 8), (1, 9), (2, 10), (3, 11), (4, 12), (5, 13), (6, 14), (7, 15)
        ]

    def update_animation(self):
        self.angle += 2
        self.position_angle += 1
        self.camera_angle += 0.5

        if self.scale_factor >= 1.5:
            self.scale_direction = -1
        elif self.scale_factor <= 0.8:
            self.scale_direction = 1
        self.scale_factor += 0.01 * self.scale_direction

        self.update()

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glClearColor(0.9, 0.9, 0.9, 1.0)

        # Настройка материалов
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 100.0)

        # Настройка освещения
        glLightfv(GL_LIGHT1, GL_POSITION, [0, 5, 0, 1.0])
        glLightfv(GL_LIGHT1, GL_SPOT_DIRECTION, [0, -1, 0])
        glLightf(GL_LIGHT1, GL_SPOT_CUTOFF, 30.0)
        glLightf(GL_LIGHT1, GL_SPOT_EXPONENT, 2.0)

        glLightfv(GL_LIGHT0, GL_POSITION, [10, 10, 10, 1])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.1, 0.1, 0.1, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslatef(0.0, 0.0, -15)
        glRotatef(self.camera_angle, 0, 1, 0)

        self.draw_ground_plane()
        self.draw_hypercube()
        self.draw_shadow()

        glFlush()

    def draw_hypercube(self):
        radius = 5.0
        x = radius * np.cos(np.radians(self.position_angle))
        z = radius * np.sin(np.radians(self.position_angle))

        glPushMatrix()
        glTranslatef(x, 0.0, z)
        glRotatef(self.angle, 1, 1, 0)
        glScalef(self.scale_factor, self.scale_factor, self.scale_factor)

        # 4D вращение
        rotation_matrix = self.rotation_matrix_4d()
        projected_vertices = [self.project_vertex(v, rotation_matrix) for v in self.vertices]

        # Отрисовка ребер
        glColor3f(0.2, 0.2, 0.8)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        for edge in self.edges:
            for idx in edge:
                glVertex3fv(projected_vertices[idx][:3].astype(np.float32).tobytes())
        glEnd()

        glPopMatrix()

    def draw_shadow(self):
        glPushMatrix()
        glColor3f(0.1, 0.1, 0.1)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        radius = 5.0
        x = radius * np.cos(np.radians(self.position_angle))
        z = radius * np.sin(np.radians(self.position_angle))

        glTranslatef(x, 0.0, z)
        glRotatef(self.angle, 1, 1, 0)

        rotation_matrix = self.rotation_matrix_4d()
        projected_vertices = [self.project_vertex(v, rotation_matrix) for v in self.vertices]

        glBegin(GL_LINES)
        for edge in self.edges:
            for idx in edge:
                vert = projected_vertices[idx].copy()
                vert[1] = -3.0
                glVertex3fv(vert[:3].astype(np.float32).tobytes())
        glEnd()

        glDisable(GL_BLEND)
        glPopMatrix()

    def draw_ground_plane(self):
        glPushMatrix()
        glTranslatef(0.0, -5.0, 0.0)
        glColor3f(0.7, 0.7, 0.7)
        glBegin(GL_QUADS)
        size = 20
        glVertex3f(-size, 0, -size)
        glVertex3f(size, 0, -size)
        glVertex3f(size, 0, size)
        glVertex3f(-size, 0, size)
        glEnd()
        glPopMatrix()

    def rotation_matrix_4d(self):
        theta = np.radians(self.angle)
        phi = np.radians(self.angle * 2)

        return np.array([
            [np.cos(theta) * np.cos(phi), -np.sin(theta), -np.sin(phi), 0],
            [np.sin(theta), np.cos(theta) * np.cos(phi), 0, -np.sin(phi)],
            [0, 0, np.cos(theta), np.sin(theta)],
            [np.sin(phi), 0, -np.sin(theta), np.cos(phi)]
        ], dtype=np.float32)

    def project_vertex(self, vertex, rotation_matrix):
        rotated = np.dot(rotation_matrix, vertex)
        perspective = 3.0 / (4.0 - rotated[3])
        return rotated[:3] * perspective


class HypercubeApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("4D Hypercube Visualization (Fixed)")
        self.setGeometry(100, 100, 800, 600)
        self.visualizer = HypercubeVisualizer()
        self.setCentralWidget(self.visualizer)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = HypercubeApp()
    window.show()
    sys.exit(app.exec_())