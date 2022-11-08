from typing import Callable
from PIL import Image
from ursina import *
from ursina.prefabs.file_browser import FileBrowser
import parameters
import utils


def _get_params():
    return parameters.SoftInstance


def set_param(name: str, value):
    print(f"Setting {name} to {value}")

    # This throws an error if the parameter doesn't exist (member doesn't exist)
    old = getattr(_get_params(), name)

    # Ensure the given value is an alright type
    if not isinstance(value, type(value)):
        raise TypeError(f"To set {name} of parameters, it must be of the same type as {old} (current value)")

    setattr(_get_params(), name, value)


def make_file_button_text(selected_file):
    return f"Select Slit Mask ({selected_file})"


def update_resolution(slider: Slider) -> float:
    """Sets the value on the slider to an appropriate resolution. Returns the new value"""
    slider.value = utils.find_nearest_2n(slider.value)
    return slider.value


class MainGui:

    def set_stopped(self):
        self.param_panel.enable = True
        self.param_panel.visible = True
        self.run_switch.value = "stop"

    def __change_sim_state(self):
        value: str = self.run_switch.value
        print("clicked:" + value)
        if value == "start":
            # Only start if the file was correct
            if self.param_panel.flush_parameters():
                # Hide the parameter panel
                self.param_panel.enable = False
                self.param_panel.visible = False

                self.start_sim()
            else:
                print("could not flush parameters")
                # Note that this actually causes __change_sim_state to be called again
                self.run_switch.value = "stop"

        elif value == "stop":
            self.param_panel.enable = True
            self.param_panel.visible = True
            self.stop_sim()
        else:
            raise AssertionError(f"Start/Stop button group should have value of start or stop, has {value}")

    def __init__(self, start_sim: Callable, stop_sim: Callable):

        self.param_panel = ParametersPanel()

        self.start_sim = start_sim
        self.stop_sim = stop_sim

        self.run_switch = ButtonGroup(("start", "stop"), default="stop", position=(.5, .5))
        self.run_switch.on_value_changed = lambda: self.__change_sim_state()


class ParametersPanel(WindowPanel):

    def flush_parameters(self) -> bool:
        """
        Flushing the parameters all at once is done so that what is seen in the GUI is always representative of the
        parameters used by the simulation.
        """

        # Note: File selector flushed when the file is selected
        if parameters.SoftInstance.occluder is None:
            print("occluder is null")
            self.file_warning.visible = True
            return False

        params = _get_params()
        params.wavelength = self.wavelength.value * 0.001  # nm to um
        params.brightnessFactor = self.brightness.value * 100
        params.tick_distance = self.tick.value * 1000  # mm to um
        params.visualizerAmount = self.visualizer_amount.value * 1
        params.detectorDistance = self.detector_distance.value * 1000  # mm to um
        params.lowResolution = self.low_res.value
        params.width = self.width.value * 1000  # mm to um
        return True

    def show_file_selector(self):
        self.file_browser.enabled = True
        self.file_browser.visible = True
        self.enabled = False  # Hide parameters panel
        self.visible = False

    def on_select_file(self, paths):
        path: Path = paths[0]
        _get_params().occluder = Image.open(path)  # Set parameter to selected image
        self.file_button.text = make_file_button_text(path.name)
        self.file_warning.visible = False  # Note it may already be false
        self.enabled = True  # Show parameters panel
        self.visible = True

    #
    def on_select_file_cancelled(self):
        self.enabled = True  # Show parameters panel
        self.visible = True
        self.file_browser.visible = False
        self.file_browser.enabled = False

    def __init__(self):
        """
        simulateFunction: function that will be called when the simulate button is called
        """

        self.file_warning = Text("A slit mask must be chosen before simulation", color=color.red, visible=False)

        self.wavelength = ThinSlider(min=500, max=10000, step=10, default=1000)  # nm
        self.brightness = ThinSlider(min=500, max=10000, step=10, default=7000)
        self.tick = ThinSlider(min=1, max=1000, step=1, default=600)

        self.file_button = Button(make_file_button_text(None))
        self.file_browser = FileBrowser(
            file_types=[".jpeg", ".jpg", ".png"],
            start_path=Path("images").resolve(),
            visible=False,  # This only shows when it is opened with the fileButton
            enable=False
        )
        # Open the file selector
        self.file_button.on_click = self.show_file_selector
        # The submit button on the file selector
        self.file_browser.on_submit = self.on_select_file
        # The close button and the little x at the corner of the file selector
        self.file_browser.cancel_button.on_click = self.on_select_file_cancelled
        self.file_browser.cancel_button_2.on_click = self.on_select_file_cancelled

        self.visualizer_amount = ThinSlider(min=1, max=10, default=3, step=1)
        self.detector_distance = ThinSlider(min=10, max=10000, default=1000, step=10)

        self.low_res = ThinSlider(min=8, max=128, step=8, default=32)
        self.low_res.on_value_changed = lambda: update_resolution(self.low_res)

        self.width = ThinSlider(min=10, max=100, step=1, default=50)  # TODO: DEFAULTS

        super().__init__(title="Simulation Parameters", position=(-.63, .5), content=(
            Text("Wavelength (nm)"),
            self.wavelength,
            Text("Tick distance (mm)"),
            self.tick,
            Text("Brightness factor"),
            self.brightness,
            self.file_button,
            Text("Number of visualizers"),
            self.visualizer_amount,
            Text("Distance to last visualizer (mm)"),
            self.detector_distance,
            Text("Resolution"),
            self.low_res,
            Text("Visualizer Width (mm)"),
            self.width
        ))
