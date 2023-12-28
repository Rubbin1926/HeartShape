import random
from math import sin, cos, pi, log
from tkinter import *

# Canvas dimensions
CANVAS_WIDTH = 640
CANVAS_HEIGHT = 480
CANVAS_CENTER_X = CANVAS_WIDTH / 2
CANVAS_CENTER_Y = CANVAS_HEIGHT / 2

# Image enlargement factor
IMAGE_ENLARGE = 11

# Heart color (China Red)
HEART_COLOR = "#ff2121"


def heart_function(t, shrink_ratio: float = IMAGE_ENLARGE):
    """
    "Heart Function Generator"
    :param shrink_ratio: Enlargement factor
    :param t: Parameter
    :return: Coordinates
    """
    # Basic function
    x = 16 * (sin(t) ** 3)
    y = -(13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))

    # Enlarge
    x *= shrink_ratio
    y *= shrink_ratio

    # Move to center of canvas
    x += CANVAS_CENTER_X
    y += CANVAS_CENTER_Y

    return int(x), int(y)


def scatter_inside(x, y, beta=0.15):
    """
    Random internal diffusion
    :param x: Original x
    :param y: Original y
    :param beta: Intensity
    :return: New coordinates
    """
    ratio_x = -beta * log(random.random())
    ratio_y = -beta * log(random.random())

    dx = ratio_x * (x - CANVAS_CENTER_X)
    dy = ratio_y * (y - CANVAS_CENTER_Y)

    return x - dx, y - dy


def shrink(x, y, ratio):
    """
    Shrink
    :param x: Original x
    :param y: Original y
    :param ratio: Ratio
    :return: New coordinates
    """
    force = -1 / ((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.6  # Magic parameter
    dx = ratio * force * (x - CANVAS_CENTER_X)
    dy = ratio * force * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy


def curve(p):
    """
    Custom curve function, adjust bounce period
    :param p: Parameter
    :return: Sin
    """
    # You can try other dynamic functions, such as Bezier, to achieve more powerful effects
    return 2 * (2 * sin(4 * p)) / (2 * pi)


class Heart:
    """
    Heart class
    """

    def __init__(self, generate_frame=20):
        self._points = set()  # Set of original heart coordinates
        self._edge_diffusion_points = set()  # Set of edge diffusion effect points
        self._center_diffusion_points = set()  # Set of central diffusion effect points
        self.all_points = {}  # Dynamic point coordinates for each frame
        self.build(2000)

        self.random_halo = 1000

        self.generate_frame = generate_frame
        for frame in range(generate_frame):
            self.calc(frame)

    def build(self, number):
        # Heart
        for _ in range(number):
            t = random.uniform(0, 2 * pi)  # Randomly avoid creating a hole in the heart
            x, y = heart_function(t)
            self._points.add((x, y))

        # Heart edge diffusion
        for _x, _y in list(self._points):
            for _ in range(3):
                x, y = scatter_inside(_x, _y, 0.05)
                self._edge_diffusion_points.add((x, y))

        # Heart inner diffusion again
        point_list = list(self._points)
        for _ in range(4000):
            x, y = random.choice(point_list)
            x, y = scatter_inside(x, y, 0.17)
            self._center_diffusion_points.add((x, y))

    @staticmethod
    def calc_position(x, y, ratio):
        # Adjust scaling ratio
        force = 1 / ((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.520  # Magic parameter

        dx = ratio * force * (x - CANVAS_CENTER_X) + random.randint(-1, 1)
        dy = ratio * force * (y - CANVAS_CENTER_Y) + random.randint(-1, 1)

        return x - dx, y - dy

    def calc(self, generate_frame):
        ratio = 10 * curve(generate_frame / 10 * pi)  # Smooth period scaling ratio

        halo_radius = int(4 + 6 * (1 + curve(generate_frame / 10 * pi)))
        halo_number = int(3000 + 4000 * abs(curve(generate_frame / 10 * pi) ** 2))

        all_points = []

        # Halo
        heart_halo_point = set()  # Set of halo point coordinates
        for _ in range(halo_number):
            t = random.uniform(0, 2 * pi)  # Randomly avoid creating a hole in the heart
            x, y = heart_function(t, shrink_ratio=11.6)  # Magic parameter
            x, y = shrink(x, y, halo_radius)
            if (x, y) not in heart_halo_point:
                # Handle new points
                heart_halo_point.add((x, y))
                x += random.randint(-14, 14)
                y += random.randint(-14, 14)
                size = random.choice((1, 2, 2))
                all_points.append((x, y, size))

        # Outline
        for x, y in self._points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 3)
            all_points.append((x, y, size))

        # Inner
        for x, y in self._edge_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))

        for x, y in self._center_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))

        self.all_points[generate_frame] = all_points

    def render(self, render_canvas, render_frame):
        for x, y, size in self.all_points[render_frame % self.generate_frame]:
            render_canvas.create_rectangle(x, y, x + size, y + size, width=0, fill=HEART_COLOR)


def draw(main: Tk, render_canvas: Canvas, render_heart: Heart, render_frame=0):
    render_canvas.delete('all')
    render_heart.render(render_canvas, render_frame)
    main.after(160, draw, main, render_canvas, render_heart, render_frame + 1)


if __name__ == '__main__':
    root = Tk()  # One Tk
    canvas = Canvas(root, bg='black', height=CANVAS_HEIGHT, width=CANVAS_WIDTH)
    canvas.pack()
    heart = Heart()  # Heart
    draw(root, canvas, heart)  # Drawing~
    root.mainloop()
