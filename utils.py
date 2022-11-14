from ursina import *
from PIL import Image


def resize_image(img: Image, size):
    img = img.resize((size, size), resample=Image.NEAREST)
    return img


def length(vec: Vec2):
    return sqrt(vec.x ** 2 + vec.y ** 2)


def get_occlusion_holes(tex: Texture) -> list[Vec2]:
    holes: list[Vec2] = []
    for x in range(0, tex.width):
        for y in range(0, tex.height):
            if tex.get_pixel(x, y).brightness < 0.5:
                # these pixels are holes
                holes.append(Vec2(x, y))

    return holes


def find_nearest_2n(f: float):
    return math.pow(2, round(math.log2(f)))


def pixel_width(vis_width: float, resolution: float):
    return vis_width / resolution
