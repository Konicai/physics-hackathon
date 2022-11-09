from ursina import Vec2, Texture

from parameters import Parameters
import utils
from dataclasses import dataclass
from typing import List, Dict
import calculations
import math


@dataclass
class Contribution:

    # The distance from the occluder pixel to the visualizer pixel
    dist: float

    vec: Vec2


class Pixel:
    def __init__(self, param: Parameters, coordinates: Vec2, separation: float, holes: List[Vec2]):
        self.coordinates: Vec2 = coordinates
        self.contributions: List[Contribution] = []
        self.totalContribution: Vec2 = Vec2(0, 0)

        pixel_width = param.width / param.resolution  # Width of each pixel, in um

        for hole in holes:
            dist_x = (coordinates.x - hole.x) * pixel_width
            dist_y = (coordinates.y - hole.y) * pixel_width

            dist = calculations.distance(dist_x, dist_y, separation)  # Distance from hole to pixel, in um

            cont = Contribution(dist, Vec2(calculations.cartesian(separation, dist, param.wavelength)))
            self.contributions.append(cont)


class Visualizer:
    def __init__(self, param: Parameters, dist: float, resolution: int, holes: List[Vec2]):
        self.distz: float = dist
        self.pixels: List[Pixel] = []

        for x in range(resolution):
            print(f"Starting row {x} for Visualizer at dist {dist}")
            for y in range(resolution):
                self.pixels.append(Pixel(param, Vec2(x, y), dist, holes))


def setup(param: Parameters) -> list[Visualizer]:
    visualizers: list[Visualizer] = []
    # Uses low res occluder
    holes: list[Vec2] = utils.get_occlusion_holes(Texture(utils.resize_image(param.occluder, param.resolution)))

    # Visualizer seperation
    vis_sep: float = param.detectorDistance / param.visualizerAmount

    for i in range(param.visualizerAmount):
        visualizers.append(
            Visualizer(param,
                       vis_sep * (i + 1),
                       param.resolution,
                       holes))

    return visualizers

# Ciaran's added code to sort the values by d-step so that the actual simulation part can run faster, will take longer to set up though
def modified_setup(param: Parameters) -> tuple[list[list[dict[Vec2, Vec2]]], list[Visualizer], int]:
    """
    returns a list where where each element represents one visualizer with a list of time steps, each time step is a
    dictionary where the keys are the coordinates to a point on the visualizer and the values are the contribution
    vectors to be added in that step. The second thing is the original big data structure
    """

    maxNumberOfSteps: int = math.ceil(calculations.distance(param.width, param.width, param.detectorDistance) / param.tick_distance)  #Max distance / distance per tick, rounded up
    planesToAddOverTime: List[List[Dict[Vec2,Vec2]]] = [] * param.visualizerAmount  # We have one big list for each visualizer

    visualizers: List[Visualizer] = setup(param)
    for visualizer in visualizers:
        # Each dict has space for a whole plane of points, and we have a dictionary for every step
        visualizerContributionPlane: List[Dict[Vec2,Vec2]] = [None] * maxNumberOfSteps
        for pixel in visualizer.pixels:
            for contribution in pixel.contributions:
                # Distance / distance per tick, rounded up
                properTimeStep: int = math.ceil(contribution.dist / param.tick_distance)
                # The contribution should be added to the plane corresponding to the above time step
                if visualizerContributionPlane[properTimeStep - 1] is None:
                    visualizerContributionPlane[properTimeStep - 1] = {pixel.coordinates: contribution.vec}
                elif pixel.coordinates in visualizerContributionPlane[properTimeStep - 1]:
                    visualizerContributionPlane[properTimeStep - 1][pixel.coordinates].x += contribution.vec.x
                    visualizerContributionPlane[properTimeStep - 1][pixel.coordinates].y += contribution.vec.y
                else:
                    visualizerContributionPlane[properTimeStep - 1][pixel.coordinates] = contribution.vec

                """
                (planesToAddOverTime[properTimeStep-1]) - acesses an element in the list which is a dictionary - darn zero indexing making it confusing
                [pixel.coordinates] - access that dictionary at key of vector being the coordinates
                
                 = contribution.vec - sets the value at this key to the contribution if it isn't defined yet
                 += contribution.vec - adds the value to the key if the value is already defined
                """
        planesToAddOverTime.append(visualizerContributionPlane)

    return planesToAddOverTime, visualizers, maxNumberOfSteps
