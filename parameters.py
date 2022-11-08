from dataclasses import dataclass

from PIL import Image

SoftInstance = None
Instance = None


@dataclass
class Parameters:
    # Generally all of these default values aren't used for the simulation. They are only used to verify the types of
    # values that are inserted into it by the GUI

    # This is also in pixels, in simulation it doesn't look like it because z is skewed
    tick_distance: float = 0.5

    wavelength: float = 0.001  # Also in pixels haha, every length unit is in pixles

    # Turn up to make brighter pixels, will probably need to be a few hundred or more to see anything
    brightnessFactor: float = 1000

    width: int = 32

    occluder: Image = None

    visualizerAmount: int = 7

    detectorDistance: float = 2000

    lowResolution: int = 16  # For all planes in time simulation

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
