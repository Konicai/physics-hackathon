import dataclasses

from ursina import Ursina, destroy, Vec3, camera, window

import parameters
from parameters_panel import MainGui
from t_sim import Simulation

app = Ursina(title="Wave Simulation")
window.fps_counter.enabled = False
window.cog_button.enabled = False

gui: MainGui = None

sim: Simulation = None


def simulate():
    global sim

    if sim is not None:
        print("Warning: simulation is already running. Not starting again")
        return

    # Shallow copy. PLI.Image appears to be immutable
    parameters.Instance = dataclasses.replace(parameters.SoftInstance)
    print("Simulation Parameters:")
    parameters.Instance.print_to_console()

    sim = Simulation()
    sim.begin()

    # After simulation has stopped, call gui.stet_stopped()


def stop_simulation():
    global sim

    if sim is None:
        print("WARNING: Tried to stop the simulation when it was not running")
        return

    sim.disable()
    sim.visible = False
    destroy(sim)
    sim.disable()
    sim.visible = False
    sim = None


if __name__ == "__main__":
    parameters.init_params()
    gui = MainGui(simulate, stop_simulation)

    cam = camera
    cam.position = Vec3(7, 7, -7)
    cam.look_at(Vec3(0, 0, 0), 'forward')
    cam.rotation_z = 0

    app.run()
