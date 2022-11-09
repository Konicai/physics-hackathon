from parameters import Parameters
import utils
from ursina import *
from dataclasses import dataclass
from typing import List, Dict
import calculations
import pickle
import math


@dataclass
class Contribution:
    dist: float
    vec: Vec2


class VisualizerPixel:
    def __init__(self, param: Parameters, coordinates: Vec2, distz: float, holes: List[Vec2]):
        self.coordinates: Vec2 = coordinates
        self.contributions: List[Contribution] = []
        self.totalContribution: Vec2 = Vec2(0, 0)

        for hole in holes:
            distance = calculations.distance((coordinates.x - hole.x) * (param.width / param.lowResolution),
                                             (coordinates.y - hole.y) * (param.width / param.lowResolution), distz)
            individualContribution: Contribution = Contribution(distance, Vec2(
                calculations.cartesian(distz, distance, param.wavelength)))
            self.contributions.append(individualContribution)


# class Visualizer: #THREADS!!!!
#     def thread_pixels(self, x, holes, resolution, distz):
#         print(f"Starting row {x} for Visualizer at dist {distz}")
#         for y in range(resolution):
#             self.pixels.append(VisualizerPixel(parameters.Instance, Vec2(x,y), distz, holes)) 

#     def __init__(self, param:Parameters, distz:float, resolution:int, holes:List[Vec2]):
#         self.distz:float = distz
#         self.pixels:List[VisualizerPixel] = []

#         p=mp.Pool(4)
#         p.starmap_async(self.thread_pixels, zip(range(0,resolution), repeat(holes), repeat(resolution), repeat(distz)))
#         p.close()
#         p.join()


class Visualizer:
    def __init__(self, param: Parameters, distz: float, resolution: int, holes: List[Vec2]):
        self.distz: float = distz
        self.pixels: List[VisualizerPixel] = []

        for x in range(resolution):
            print(f"Starting row {x} for Visualizer at dist {distz}")
            for y in range(resolution):
                self.pixels.append(VisualizerPixel(param, Vec2(x, y), distz, holes))


def setUpTimeState(param: Parameters, cache=0, usecache=0) -> List[Visualizer]:
    visualizers: List[Visualizer] = []
    if usecache == 0:  # if no use cache
        lowResHoles: List[Vec2] = utils.get_occlusion_holes(
            Texture(utils.resize_image(param.occluder, param.lowResolution)))  # Uses low res occluder
        print(lowResHoles)
        for i in range(param.visualizerAmount):
            visualizers.append(
                Visualizer(param, param.detectorDistance / param.visualizerAmount * (i + 1), param.lowResolution,
                           lowResHoles))

        if cache == 1:
            # cache if needed
            f = open("cache.pkl", "wb")
            cache = pickle.dump(visualizers, f)
            print("cache written")
            f.close()

    else:  # if yee cache
        # check for cache
        file = None
        try:
            file = open("cache.pkl", "rb")
        except:
            # cache is not there:
            print("cache does not exist")
            visualizers = setUpTimeState(param, cache=cache, usecache=0)
        else:
            visualizers = (pickle.load(file))
            file.close()
            print("cache got")

    return visualizers


# Ciaran's added code to sort the values by d-step so that the actual simulation part can run faster, will take longer to set up though
def modifiedSetUpTimeState(param: Parameters) -> tuple[list[list[dict[Vec2, Vec2]]], list[Visualizer], int]:
    """
    returns a list where where each element represents one visualizer with a list of time steps, each time step is a
    dictionary where the keys are the coordinates to a point on the visualizer and the values are the contribution
    vectors to be added in that step. The second thing is the original big data structure
    """

    maxNumberOfSteps: int = math.ceil(calculations.distance(param.width, param.width, param.detectorDistance) / param.tick_distance)  #Max distance / distance per tick, rounded up
    planesToAddOverTime: List[List[Dict[Vec2,Vec2]]] = [] * param.visualizerAmount  # We have one big list for each visualizer

    visualizers: List[Visualizer] = setUpTimeState(param)
    for visualizer in visualizers:
        visualizerContributionPlane: List[Dict[Vec2,Vec2]] = [None] * maxNumberOfSteps #Each dict has space for a whole plane of points, and we have a dictionary for every step
        for pixel in visualizer.pixels:
            for contribution in pixel.contributions:
                # Distance / distance per tick, rounded up
                properTimeStep: int = math.ceil(contribution.dist / param.tick_distance)
                # The contribution should be added to the plane corresponding to the above time step
                if visualizerContributionPlane[properTimeStep - 1] is None:
                    visualizerContributionPlane[properTimeStep - 1] = dict()
                    visualizerContributionPlane[properTimeStep - 1][pixel.coordinates] = contribution.vec
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
