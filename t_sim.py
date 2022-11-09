from ursina import *
from PIL import Image
import utils
import parameters
import set_up_state
from typing import List, Dict
from set_up_state import Visualizer


class Simulation(Entity):
    def __init__(self):
        super().__init__()
        self.currentTick = 0
        self.currentTickDistance = 0
        self.zoffset = 2
        self.visualisers = []

        self.visgroup: List[Entity] = []
        self.occluder = None

    def create_occluder(self, tex: Image) -> Entity:
        return Entity(model='plane', texture=Texture(tex), position=Vec3(0, self.zoffset, 0))

    def create_visualisers(self, visuals):
        vis = []
        for i, v in enumerate(visuals, start=1):
            spacing = 4 / len(
                visuals)  # TODO - The length is distorted from the value in parameters - not sure what a good fix is

            if i != len(visuals):
                tex = Texture(
                    Image.new(mode="RGBA", size=(parameters.Instance.resolution, parameters.Instance.resolution), color=(255, 0, 0, 100)))
                plane = Entity(model='plane', texture=tex, position=(0, self.zoffset - i * spacing, 0))

            else:  # special case for final visualiser AKA detector
                tex = Texture(
                    Image.new(mode="RGBA", size=(parameters.Instance.resolution, parameters.Instance.resolution), color=(0, 0, 0, 255)))
                plane = Entity(model='plane', texture=tex, position=(0, self.zoffset - i * spacing, 0))

            vis.append(plane)
        return vis

    def begin(self):
        self.planes_to_add: List[List[Dict[Vec2, Vec2]]]
        self.visualisers: List[Visualizer]
        self.last_tick: int

        (self.planes_to_add, self.visualisers, self.last_tick) = set_up_state.modified_setup(parameters.Instance)

        self.occluder = self.create_occluder(parameters.Instance.occluder)
        self.visgroup += (self.create_visualisers(self.visualisers))

        print("begun")

    # update every pixel of every visualizer to add any waves that have reached it
    def update(self):
        if math.ceil(self.currentTickDistance / parameters.Instance.tick_distance) <= self.last_tick:
            t = time.perf_counter()
            print(f"update frame {self.currentTick} of {self.last_tick}")
            for i, visualizer in enumerate(self.visualisers):
                vis_plane_to_add = self.planes_to_add[i]
                # Putting this here so it doesn't have to do an extra accessing element on a list every time
                var = math.ceil(self.currentTickDistance / parameters.Instance.tick_distance) - 1  # speedy
                for vis_pixel in visualizer.pixels:

                    # Newer faster code for modified set up function
                    if (vis_plane_to_add[var] is not None) and (vis_pixel.coordinates in vis_plane_to_add[var]):

                        vis_pixel.totalContribution += vis_plane_to_add[var][vis_pixel.coordinates]

                    '''
                    [i] - acesses the visualizer
                    [math.ceil(self.currenttickdistance / parameters.Instance.tick_distance)] - acesses the dictionary for the given distance step
                    [visualizerPixel.coordinates] - acesses the key that is the position vector of the pixel on the visualizer (the value is the contribution to add for that frame)
                    '''

                    # color pixels
                    v = self.visgroup[i]
                    b = min(int(utils.length(vis_pixel.totalContribution) * parameters.Instance.brightnessFactor), 255)
                    v.texture.set_pixel(int(vis_pixel.coordinates.x), int(vis_pixel.coordinates.y), rgb(b, b, b))
                    v.texture.apply()

            print(time.perf_counter() - t)
            self.currentTick += 1
            self.currentTickDistance += parameters.Instance.tick_distance

        # Then just need to draw it on the screen now that the pixel values are updated
