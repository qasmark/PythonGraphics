import pygame
import moderngl
import numpy as np
from pyrr import Matrix44, Vector3
import random
import math
import time

fibonacci_numbers = [1, 1]
num_squares = 15
for i in range(2, num_squares):
    fibonacci_numbers.append(fibonacci_numbers[-1] + fibonacci_numbers[-2])

square_colors = [(random.random(), random.random(), random.random()) for _ in range(num_squares)]

pygame.init()
screen = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)
clock = pygame.time.Clock()
ctx = moderngl.create_context()

vertex_shader = '''
#version 330
in vec3 in_position;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
void main() {
    gl_Position = projection * view * model * vec4(in_position, 1.0);
}
'''

fragment_shader = '''
#version 330
out vec4 fragColor;
uniform vec3 color;
void main() {
    fragColor = vec4(color, 1.0);
}
'''

prog = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

vertices = np.array([
    -0.5, -0.5, 0.0,
     0.5, -0.5, 0.0,
     0.5,  0.5, 0.0,
    -0.5,  0.5, 0.0
], dtype='f4')

vbo = ctx.buffer(vertices)
vao = ctx.vertex_array(prog, [(vbo, '3f', 'in_position')])

view = Matrix44.look_at(Vector3([0, 0, 1000]), Vector3([0, 0, 0]), Vector3([0, 1, 0]))
projection = Matrix44.perspective_projection(45.0, 800/600, 0.1, 2000.0)

prog['view'].write(view.astype('f4').tobytes())
prog['projection'].write(projection.astype('f4').tobytes())

def draw_square(x, y, z, size, angle, color):
    model = Matrix44.from_translation(Vector3([x, y, z])) * Matrix44.from_scale(Vector3([size, size, 1.0])) * Matrix44.from_z_rotation(angle)
    prog['model'].write(model.astype('f4').tobytes())
    prog['color'].value = color
    vao.render(moderngl.TRIANGLE_FAN)

def draw_spiral_arc(x, y, z, radius, start_angle, end_angle):
    segments = 50
    theta = np.linspace(start_angle, start_angle + math.pi / 2, segments)
    arc_vertices = np.array([
        (x + radius * math.cos(t), y + radius * math.sin(t), z + t * 10) for t in theta
    ], dtype='f4').flatten()

    arc_vbo = ctx.buffer(arc_vertices)
    arc_vao = ctx.simple_vertex_array(prog, arc_vbo, 'in_position')
    prog['color'].value = (1.0, 1.0, 1.0)
    arc_vao.render(moderngl.LINE_STRIP)

def main():
    running = True
    local_angle = 0
    x, y, z = 0, 0, 0
    current_step = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ctx.clear(0.0, 0.0, 0.0)

        for i in range(min(current_step + 1, len(fibonacci_numbers))):
            size = fibonacci_numbers[i] * 10
            color = square_colors[i]

            draw_square(x, y, z, size, local_angle, color)

            radius = size / 2
            draw_spiral_arc(x, y, z, radius, local_angle, local_angle + math.pi / 2)

            x += radius * 2 * math.cos(local_angle)
            y += radius * 2 * math.sin(local_angle)
            z += math.pi / 2 * 10
            local_angle += math.pi / 2

        if current_step < len(fibonacci_numbers) - 1:
            current_step += 1
            time.sleep(1)

        pygame.display.flip()
        clock.tick(10)

    pygame.quit()

if __name__ == "__main__":
    main()