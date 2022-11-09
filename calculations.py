import math
from ursina import Vec2
"""
using variables from parameter file

"""


# distance calculation
def distance(dx: float, dy: float, dz: float) -> float:
    return math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)


# angle calculation
def angle(wavelength: float, ray_distance: float) -> float:
    return (ray_distance % wavelength) / wavelength * 2 * math.pi


# Calculation for wave amplitude
def amplitude(vis_separation: float, dist: float) -> float:
    return (1 + vis_separation / dist) / dist


# Calculating pixel color values
def cartesian(vis_separation: float, ray_distance: float, wavelength: float) -> Vec2:
    amp = amplitude(vis_separation, ray_distance)
    ang = angle(wavelength, ray_distance)
    x = amp * math.cos(ang)
    y = amp * math.sin(ang)
    return Vec2(x, y)



