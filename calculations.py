from math import cos, sin, sqrt, pi
from ursina import Vec2
"""
using variables from parameter file

"""


# distance calculation
def distance(dx: float, dy: float, dz: float) -> float:
    return sqrt(dx ** 2 + dy ** 2 + dz ** 2)


# angle calculation
def angle(wavelength: float, ray_dist: float) -> float:
    # the wavelength (λ) travels along the ray distance

    #               Ray distance
    # |---------------------------------------|
    # |-----λ-----|-----λ-----|-----λ-----|---|
    #                                       ^
    #                              (ray_distance % λ)

    # Measure of how close the wave is to ending on an n * λ, in terms of phase angle
    return (ray_dist % wavelength) / wavelength * (2 * pi)


# Calculation for wave amplitude
def amplitude(vis_separation: float, ray_dist: float) -> float:
    return (1 + vis_separation / ray_dist) / ray_dist


# Calculating pixel color values
def cartesian(vis_separation: float, ray_dist: float, wavelength: float) -> Vec2:
    amp = amplitude(vis_separation, ray_dist)
    ang = angle(wavelength, ray_dist)
    x = amp * cos(ang)
    y = amp * sin(ang)
    return Vec2(x, y)



