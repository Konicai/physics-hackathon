from dataclasses import dataclass

from PIL import Image

SoftInstance = None
Instance = None


@dataclass
class Parameters:
    # Generally all of these default values aren't used for the simulation. They are only used to verify the types of
    # values that are inserted into it by the GUI

    # Micrometers (um)
    tick_distance: float = 0.5

    # Micrometers (um)
    wavelength: float = 0.001

    # Turn up to make brighter pixels, will probably need to be a few hundred or more to see anything
    brightnessFactor: float = 1000

    width: int = 32 # Width of visualizer in um

    occluder: Image = None

    # Amount of visualizers
    visualizerAmount: int = 7

    # Distance from the occluder to the final visualizer, in um
    detectorDistance: float = 2000

    # Number of pixels along the length of each visualizer
    resolution: int = 16  # For all planes in time simulation

    def print_to_console(self):

        print()
        for attr in dir(self):
            if not attr.startswith("__") and not attr == "printToConsole":
                print(f"{attr}: {getattr(self, attr)}")

        print()


def init_params():
    global SoftInstance, Instance

    if SoftInstance is None:
        SoftInstance = Parameters()

    if Instance is None:
        Instance = Parameters()
