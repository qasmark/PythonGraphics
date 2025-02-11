import random
import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# --- Константы ---
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
DICE_TYPES = {
    4: "Tetrahedron",
    6: "Cube"
}
DEFAULT_DICE_TYPE = 6
RESTITUTION = 0.6
FRICTION = 0.8
STABLE_THRESHOLD = 0.98

# --- Цвета ---
WHITE = (1, 1, 1)
BLACK = (0, 0, 0)
RED = (1, 0, 0)
GREEN = (0, 1, 0)
BLUE = (0, 0, 1)
GRAY = (0.5, 0.5, 0.5)
DARK_GRAY = (0.2, 0.2, 0.2)

# --- Параметры камеры ---
MOUSE_SENSITIVITY = 0.1
MOVE_SPEED = 0.2

# --- Skybox ---
SKYBOX_RADIUS = 50  # Радиус скайбокса


# --- Классы ---

class Dice:
    def __init__(self, num_sides, size=1.0):
        self.num_sides = num_sides
        self.size = size
        self.vertices = []
        self.faces = []
        self.normals = []
        self.colors = []
        self.rotation = [0, 0, 0]
        self.position = [0, 0, 0]
        self.velocity = [0, 0, 0]
        self.angular_velocity = [0, 0, 0]
        self.is_rolling = False
        self.result = 0
        self.create_geometry()
        self.number_vertices = {}
        self.generate_number_vertices()
        self.is_sleeping = False
        self.grounded_timer = 0

        if self.num_sides == 4:
            self.mass = 0.8
        elif self.num_sides == 6:
            self.mass = 1.0
        else:
            self.mass = 1.0

        self.inertia_tensor = self.calculate_inertia_tensor()
        self.inv_inertia_tensor = self.calculate_inverse_inertia_tensor()

    def calculate_inertia_tensor(self):
        if self.num_sides == 6:
            i = (1 / 6) * self.mass * self.size ** 2
            return [[i, 0, 0], [0, i, 0], [0, 0, i]]
        elif self.num_sides == 4:
            i = (1 / 20) * self.mass * self.size ** 2 * 5
            return [[i, 0, 0], [0, i, 0], [0, 0, i]]
        return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

    def calculate_inverse_inertia_tensor(self):
        tensor = self.calculate_inertia_tensor()
        inv_tensor = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        for i in range(3):
            if tensor[i][i] != 0:
                inv_tensor[i][i] = 1.0 / tensor[i][i]
        return inv_tensor

    def create_geometry(self):
        if self.num_sides == 4:
            s = self.size
            self.vertices = [
                (s, s, s), (s, -s, -s), (-s, s, -s), (-s, -s, s)
            ]
            self.faces = [
                (0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)
            ]
            self.normals = [
                self.calculate_normal(self.vertices[f[0]], self.vertices[f[1]], self.vertices[f[2]])
                for f in self.faces
            ]
            self.colors = [RED, GREEN, BLUE, WHITE]

        elif self.num_sides == 6:
            s = self.size / 2
            self.vertices = [
                (s, s, -s), (s, -s, -s), (-s, -s, -s), (-s, s, -s),
                (s, s, s), (s, -s, s), (-s, -s, s), (-s, s, s)
            ]
            self.faces = [
                (0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4),
                (2, 3, 7, 6), (0, 3, 7, 4), (1, 2, 6, 5)
            ]
            self.normals = [
                self.calculate_normal(self.vertices[f[0]], self.vertices[f[1]], self.vertices[f[2]])
                for f in self.faces
            ]
            self.colors = [
                RED, GREEN, BLUE, WHITE,
                (1, 0.5, 0), (0, 0.5, 1), (0.5, 0, 1), (1, 1, 0)
            ]

    def calculate_normal(self, v1, v2, v3):
        edge1 = (v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2])
        edge2 = (v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2])
        normal = (
            edge1[1] * edge2[2] - edge1[2] * edge2[1],
            edge1[2] * edge2[0] - edge1[0] * edge2[2],
            edge1[0] * edge2[1] - edge1[1] * edge2[0]
        )
        length = math.sqrt(normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2)
        if length == 0: return (0, 0, 0)
        return (normal[0] / length, normal[1] / length, normal[2] / length)

    def generate_number_vertices(self):
        self.number_vertices = {
            '1': [(0, -1), (0, 1)],
            '2': [(-0.5, 1), (0.5, 1), (0.5, 0), (-0.5, 0), (-0.5, -1), (0.5, -1)],
            '3': [(-0.5, 1), (0.5, 1), (0.5, 0), (-0.5, 0), (0.5, 0), (0.5, -1), (-0.5, -1)],
            '4': [(-0.5, 1), (-0.5, 0), (0.5, 0), (0.5, 1), (0.5, -1)],
            '5': [(0.5, 1), (-0.5, 1), (-0.5, 0), (0.5, 0), (0.5, -1), (-0.5, -1)],
            '6': [(0.5, 1), (-0.5, 1), (-0.5, -1), (0.5, -1), (0.5, 0), (-0.5, 0)]
        }

    def draw(self):
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)

        for i, face in enumerate(self.faces):
            glBegin(GL_POLYGON)
            glNormal3fv(self.normals[i % len(self.normals)])
            for vertex_index in face:
                glColor3fv(self.colors[vertex_index])
                glVertex3fv(self.vertices[vertex_index])
            glEnd()

        if self.is_rolling == False and not self.is_sleeping:
            self.draw_numbers()

        glPopMatrix()

    def draw_numbers(self):
        glColor3fv(BLACK)

        for i, face in enumerate(self.faces):
            centroid = [0, 0, 0]
            for vertex_index in face:
                for j in range(3):
                    centroid[j] += self.vertices[vertex_index][j]
            for j in range(3):
                centroid[j] /= len(face)

            if self.num_sides == 4:
                offset = [n * 0.15 * self.size for n in self.normals[i]]
            else:
                offset = [n * 0.3 * self.size for n in self.normals[i % len(self.normals)]]
            text_pos = [centroid[j] + offset[j] for j in range(3)]

            glPushMatrix()
            glTranslatef(text_pos[0], text_pos[1], text_pos[2])
            glRotatef(-self.rotation[2], 0, 0, 1)
            glRotatef(-self.rotation[1], 0, 1, 0)
            glRotatef(-self.rotation[0], 1, 0, 0)
            scale_factor = 0.1 * self.size
            if self.num_sides == 6: scale_factor = 0.2 * self.size
            glScalef(scale_factor, scale_factor, scale_factor)
            self.draw_number_lines(str(i + 1))
            glPopMatrix()

    def draw_number_lines(self, number_str):
        if number_str in self.number_vertices:
            glBegin(GL_LINES)
            for vertex in self.number_vertices[number_str]:
                glVertex3f(vertex[0], vertex[1], 0)
            glEnd()

    def start_roll(self, initial_velocity, initial_angular_velocity):
        self.velocity = initial_velocity
        self.angular_velocity = initial_angular_velocity
        self.is_rolling = True
        self.result = 0
        self.is_sleeping = False
        self.grounded_timer = 0

    def update(self, dt, plane_y=-2):
        if self.is_sleeping:
            return

        if not self.is_rolling:
            return

        # --- Гравитация ---
        self.velocity[1] += -9.81 * dt

        # --- Обновление позиции ---
        for i in range(3):
            self.position[i] += self.velocity[i] * dt

        # --- Обновление вращения ---
        for i in range(3):
            self.rotation[i] += self.angular_velocity[i] * dt
        self.rotation = [r % 360 for r in self.rotation]

        # --- Столкновение с полом ---
        closest_vertex = None
        min_distance = float('inf')

        for vertex in self.vertices:
            rotated_vertex = self.rotate_point(vertex, self.rotation)
            world_vertex = [self.position[i] + rotated_vertex[i] for i in range(3)]
            distance = world_vertex[1] - plane_y
            if distance < min_distance:
                min_distance = distance
                closest_vertex = world_vertex
                local_vertex = rotated_vertex

        if min_distance < 0.01:
            normal = [0, 1, 0]
            relative_velocity = [self.velocity[i] + (
                    self.angular_velocity[(i + 1) % 3] * local_vertex[(i + 2) % 3] -
                    self.angular_velocity[(i + 2) % 3] * local_vertex[(i + 1) % 3]) for i in range(3)]
            dot_product = sum(relative_velocity[i] * normal[i] for i in range(3))

            if dot_product < 0:
                impulse = -(1 + RESTITUTION) * dot_product
                impulse /= (1.0 / self.mass)
                MAX_IMPULSE = 10.0
                impulse = min(impulse, MAX_IMPULSE)

                # --- Линейная скорость ---
                for i in range(3):
                    self.velocity[i] += (impulse / self.mass) * normal[i]

                # --- Трение ---
                tangent_velocity = [relative_velocity[i] - dot_product * normal[i] for i in range(3)]
                tangent_magnitude = math.sqrt(sum(v ** 2 for v in tangent_velocity))

                if tangent_magnitude > 1e-6:
                    tangent_direction = [v / tangent_magnitude for v in tangent_velocity]
                    friction_impulse = min(impulse * FRICTION, tangent_magnitude)
                    cross_product = [
                        local_vertex[1] * normal[2] - local_vertex[2] * normal[1],
                        local_vertex[2] * normal[0] - local_vertex[0] * normal[2],
                        local_vertex[0] * normal[1] - local_vertex[1] * normal[0]
                    ]
                    angular_impulse = [cross_product[i] * impulse for i in range(3)]
                    friction_torque = [cross_product[i] * friction_impulse for i in range(3)]

                    for i in range(3):
                        for j in range(3):
                            self.angular_velocity[i] += self.inv_inertia_tensor[i][j] * (
                                    angular_impulse[j] - friction_torque[j])
                else:
                    self.angular_velocity = [0, 0, 0]

                penetration_depth = -min_distance
                self.position[1] += penetration_depth
                bounce_sound.play()

                # --- Расчет и вывод энергии ---
                kinetic_energy_linear = 0.5 * self.mass * sum(v ** 2 for v in self.velocity)
                kinetic_energy_angular = 0.5 * sum(
                    self.inertia_tensor[i][i] * self.angular_velocity[i] ** 2 for i in range(3)
                )
                total_energy = kinetic_energy_linear + kinetic_energy_angular
                print(
                    f"Energy: {total_energy:.4f}, Vel: {[round(v, 3) for v in self.velocity]}, AngVel: {[round(av, 3) for av in self.angular_velocity]}")

            self.grounded_timer += dt

        else:
            self.grounded_timer = 0

        # --- Проверка остановки ---
        if self.grounded_timer > 0.1 and self.is_stable() and all(
                abs(v) < 0.1 for v in self.velocity) and all(abs(av) < 0.5 for av in self.angular_velocity):
            self.is_rolling = False
            self.is_sleeping = True
            self.determine_result()

    def is_stable(self):
        up_vector = (0, 1, 0)
        for normal in self.normals:
            rotated_normal = self.rotate_point(normal, self.rotation)
            dot_product = sum(rotated_normal[i] * up_vector[i] for i in range(3))
            if dot_product >= STABLE_THRESHOLD:
                return True
        return False

    def rotate_point(self, point, rotation):
        x, y, z = point
        rx, ry, rz = [math.radians(r) for r in rotation]

        y1 = y * math.cos(rx) - z * math.sin(rx)
        z1 = y * math.sin(rx) + z * math.cos(rx)
        y, z = y1, z1

        x1 = x * math.cos(ry) + z * math.sin(ry)
        z1 = -x * math.sin(ry) + z * math.cos(ry)
        x, z = x1, z1

        x1 = x * math.cos(rz) - y * math.sin(rz)
        y1 = x * math.sin(rz) + y * math.cos(rz)
        x, y = x1, y1

        return [x, y, z]

    def determine_result(self):
        if self.num_sides == 4:
            upward_vector = (0, -1, 0)
            min_dot = 2  # максимально близкая грань к вектору "вниз"
            self.result = 1

            for i, normal in enumerate(self.normals):
                rotated_normal = self.rotate_point(normal, self.rotation)
                dot_product = rotated_normal[0] * upward_vector[0] + rotated_normal[1] * upward_vector[1] + \
                              rotated_normal[2] * upward_vector[2]
                if 1 - dot_product < min_dot:
                    min_dot = 1 - dot_product
                    self.result = i + 1

        elif self.num_sides == 6:
            upward_vector = (0, 1, 0)  # Вектор, указывающий "вверх"
            max_dot = -2  # Максимально близкая грань к вектору "вверх"
            self.result = 1

            for i, normal in enumerate(self.normals):
                rotated_normal = self.rotate_point(normal, self.rotation)
                dot_product = rotated_normal[0] * upward_vector[0] + rotated_normal[1] * upward_vector[1] + \
                              rotated_normal[2] * upward_vector[2]
                if dot_product > max_dot:
                    max_dot = dot_product
                    self.result = i + 1

        print(f"Result: {self.result}")


# --- Функции ---

def init():
    glClearColor(0.9, 0.9, 0.9, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)

    glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
    glMaterialfv(GL_FRONT, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
    glMaterialfv(GL_FRONT, GL_SHININESS, 50.0)

    glLightfv(GL_LIGHT0, GL_POSITION, [2, 5, 2, 1])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.7, 0.7, 0.7, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, [-2, -5, -2])
    glLightfv(GL_LIGHT0, GL_SPOT_CUTOFF, 30.0)
    glLightfv(GL_LIGHT0, GL_SPOT_EXPONENT, 2.0)


def draw_infinite_plane(size=100, grid_size=5):
    glBegin(GL_QUADS)
    glColor3fv(GRAY)
    glNormal3f(0, 1, 0)
    glVertex3f(-size, -2, -size)
    glVertex3f(size, -2, -size)
    glVertex3f(size, -2, size)
    glVertex3f(-size, -2, size)
    glEnd()

    glColor3fv(DARK_GRAY)
    glLineWidth(1.0)
    glBegin(GL_LINES)
    for i in range(-size, size + 1, grid_size):
        glVertex3f(i, -2, -size)
        glVertex3f(i, -2, size)
        glVertex3f(-size, -2, i)
        glVertex3f(size, -2, i)
    glEnd()


def load_texture(filename):
    """Загружает текстуру из файла и возвращает её ID."""
    try:
        image = pygame.image.load(filename)
        texture_data = pygame.image.tostring(image, "RGBA", 1)
        width, height = image.get_size()

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        return texture_id
    except pygame.error as e:
        print(f"Error loading texture {filename}: {e}")
        return None


def draw_skybox(radius, texture_id):
    """Рисует сферический скайбокс."""

    glDisable(GL_LIGHTING)
    glDepthMask(GL_FALSE)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glEnable(GL_TEXTURE_2D)

    quadric = gluNewQuadric()
    gluQuadricTexture(quadric, GL_TRUE)
    gluQuadricNormals(quadric, GLU_SMOOTH)
    gluSphere(quadric, radius, 32, 32)
    gluDeleteQuadric(quadric)

    glDisable(GL_TEXTURE_2D)
    glDepthMask(GL_TRUE)
    glEnable(GL_LIGHTING)


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # --- Камера ---
    glRotatef(camera_pitch, 1, 0, 0)
    glRotatef(camera_yaw, 0, 1, 0)
    glTranslatef(-camera_x, -camera_y, -camera_z)

    # --- Скайбокс ---
    draw_skybox(SKYBOX_RADIUS, skybox_texture)

    draw_infinite_plane()
    dice.draw()

    pygame.display.flip()


def reshape(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (width / height), 0.1, 1000.0)
    glMatrixMode(GL_MODELVIEW)


def handle_input():
    global dice, current_dice_type, camera_x, camera_y, camera_z, camera_yaw, camera_pitch, flying_mode

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == K_SPACE:
                if not dice.is_rolling:
                    initial_velocity = [random.uniform(-5, 5), random.uniform(8, 12), random.uniform(-5, 5)]
                    initial_angular_velocity = [random.uniform(-180, 180), random.uniform(-180, 180),
                                                random.uniform(-180, 180)]
                    dice.start_roll(initial_velocity, initial_angular_velocity)
            elif event.key == K_r:
                dice = Dice(current_dice_type, size=1.5)
                dice.position = [0, 3, 0]
            elif event.key == K_1:
                current_dice_type = 4
                dice = Dice(current_dice_type, size=1.5)
                dice.position = [0, 3, 0]
                print("Switched to Tetrahedron")
            elif event.key == K_2:
                current_dice_type = 6
                dice = Dice(current_dice_type, size=1.5)
                dice.position = [0, 3, 0]
                print("Switched to Cube")
            elif event.key == K_f:
                flying_mode = not flying_mode
                pygame.mouse.set_visible(not flying_mode)
                if flying_mode:
                    pygame.mouse.set_pos(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
                print(f"Flying mode: {flying_mode}")

    if flying_mode:
        mouse_dx, mouse_dy = pygame.mouse.get_rel()
        camera_yaw += mouse_dx * MOUSE_SENSITIVITY
        camera_pitch += mouse_dy * MOUSE_SENSITIVITY
        camera_pitch = max(-89, min(89, camera_pitch))
        pygame.mouse.set_pos(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

        keys = pygame.key.get_pressed()
        speed = MOVE_SPEED

        forward_x = -math.sin(math.radians(camera_yaw)) * math.cos(math.radians(camera_pitch))
        forward_y = math.sin(math.radians(camera_pitch))
        forward_z = -math.cos(math.radians(camera_yaw)) * math.cos(math.radians(camera_pitch))
        right_x = math.sin(math.radians(camera_yaw - 90))
        right_z = math.cos(math.radians(camera_yaw - 90))
        up_x = 0
        up_y = 1
        up_z = 0

        if keys[K_w]:
            camera_x += forward_x * speed
            camera_y += forward_y * speed
            camera_z += forward_z * speed
        if keys[K_s]:
            camera_x -= forward_x * speed
            camera_y -= forward_y * speed
            camera_z -= forward_z * speed
        if keys[K_a]:
            camera_x += right_x * speed
            camera_z += right_z * speed
        if keys[K_d]:
            camera_x -= right_x * speed
            camera_z -= right_z * speed
        if keys[K_q]:
            camera_y -= up_y * speed
        if keys[K_e]:
            camera_y += up_y * speed


def main():
    global dice, current_dice_type, bounce_sound, camera_x, camera_y, camera_z, camera_yaw, camera_pitch, flying_mode, skybox_texture
    pygame.init()
    pygame.mixer.init()
    bounce_sound = pygame.mixer.Sound("bounce.wav")

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Dice Rolling Simulation")
    current_dice_type = DEFAULT_DICE_TYPE
    dice = Dice(current_dice_type, size=1.5)
    dice.position = [0, 3, 0]

    camera_x = 0
    camera_y = 3
    camera_z = -10
    camera_yaw = 0
    camera_pitch = 20
    flying_mode = False

    skybox_texture = load_texture("sky.jpg")
    if skybox_texture is None:
        pygame.quit()
        sys.exit()

    init()
    reshape(WINDOW_WIDTH, WINDOW_HEIGHT)

    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(60) / 1000.0
        substeps = 5
        physics_dt = dt / substeps

        handle_input()

        for _ in range(substeps):
            dice.update(physics_dt)
        display()


if __name__ == "__main__":
    main()