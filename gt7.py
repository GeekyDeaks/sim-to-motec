import PySimpleGUI as sg
import json
import os
import time

from stm.version import __version__
from stm.gt7 import GT7Logger, GT7Sampler
from logging import getLogger, basicConfig, DEBUG

# try and load the sate
STATE_FILE = "gt7.cfg"

state = {
    "IP": "255.255.255.255",
    "PORT": 33740,
    "REPLAY": False,
    "DRIVER": "",
    "SESSION": "",
    "IMPERIAL": False

}

try:
    with open(STATE_FILE) as f:
        state.update(json.load(f))
except Exception as e:
    pass

sg.change_look_and_feel('Default1')
sg.set_options(font="Arial 12")

BUTTON_DISABLED = (sg.theme_background_color(), sg.theme_background_color())
BUTTON_ENABLED = (sg.theme_button_color_text(), sg.theme_background_color())

labels = [
    [sg.Text("PS IP Address")],
    [sg.Text("Local UDP Port")],
    [sg.Text("Capture Replays")],
    [sg.Text("Imperial Units")],
    [sg.Text("Driver")],
    [sg.Text("Session")],
    [sg.Text("Log File")],
    [sg.Text("Vehicle")],
    [sg.Text("Venue")],
    [sg.Text("Tick")],
    [sg.Text("Lap")],
]

values = [
    [sg.Input(state["IP"], key="IP", size=(15,1), enable_events=True)],
    [sg.Input(state["PORT"], key="PORT", size=(15,1), enable_events=True), sg.Text("Only change this if using a UDP relay", font="arial 12 italic")],
    [sg.Checkbox("", state["REPLAY"], key="REPLAY", enable_events=True)],
    [sg.Checkbox("", state["IMPERIAL"], key="IMPERIAL", enable_events=True)],
    [sg.Input(state["DRIVER"], key="DRIVER", size=(15,1), enable_events=True )],
    [sg.Input(state["SESSION"], key="SESSION", size=(15,1), enable_events=True )],
    [sg.Text("Not Started",key="LOGFILE" )],
    [sg.Text("N/A", key="VEHICLE")],
    [sg.Text("N/A", key="VENUE")],
    [sg.Text("N/A", key="TICK")],
    [sg.Text("N/A", key="LAP")],
]

# Define the window's contents
layout = [
    [sg.Column(labels, element_justification='r'), sg.Column(values)],
    [
        sg.Button('Start', key="START"), 
        sg.Button("Stop", key="STOP", disabled=True, button_color=BUTTON_DISABLED), 
        sg.Button('Quit', key="QUIT"),
        sg.Checkbox("Rawfile", key="RAWFILE")
     ],
    [sg.HorizontalSeparator()],
    [sg.Output(size=(100, 12), echo_stdout_stderr=True)]     
]

# Create the window
window = sg.Window(f"GT7 logger v{__version__}", layout, finalize=True)
# start the logger after creating the output element
basicConfig(
     level=DEBUG,
     format="%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s",
     datefmt="%H:%M:%S"
)
l = getLogger(__name__)

logger = None

# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read(timeout=500)
    # See if user wants to quit or window was closed
    if event in (sg.WINDOW_CLOSED, "QUIT"):
        break

    if event == "IP" and len(values['IP']) and values['IP'][-1] not in ('.1234567890'):
        window["IP"].update(values['IP'][:-1])

    if event == "PORT" and len(values['PORT']) and values['PORT'][-1] not in ('1234567890'):
        window["PORT"].update(values['PORT'][:-1])

    if event in state:
        state[event] = values[event]

    if event == "START":
        filetemplate = os.path.join("logs", "gt7", "{venue}_{vehicle}_{driver}_{session}_{datetime}")

        if values["RAWFILE"]:
            rawfile = os.path.join("logs", "raw", "gt7", f"{time.time():.0f}.db" )
        else:
            rawfile = None

        logger = GT7Logger(
            rawfile=rawfile,
            sampler=GT7Sampler(addr=values["IP"], port=values["PORT"], freq=60),
            filetemplate=filetemplate,
            replay=values["REPLAY"],
            driver=values["DRIVER"],
            session=values["SESSION"],
            imperial=values["IMPERIAL"]
        )
        logger.start()

    if event == "STOP" and logger:
        logger.stop()
        logger.join()
        logger = None

    if logger:
        window["QUIT"].update(disabled=True, button_color=BUTTON_DISABLED)
        window["START"].update(disabled=True, button_color=BUTTON_DISABLED)
        window["STOP"].update(disabled=False, button_color=BUTTON_ENABLED)
        window["LOGFILE"].update(logger.filename)
        # update with values
        if logger.last_packet:
            p = logger.last_packet
            window["LAP"].update( f"{p.current_lap}/{p.laps}" )
            window["TICK"].update(f"{p.tick}")
            window["VEHICLE"].update(logger.get_vehicle())
            window["VENUE"].update(logger.get_venue())


    else:
        window["QUIT"].update(disabled=False, button_color=BUTTON_ENABLED)
        window["START"].update(disabled=False, button_color=BUTTON_ENABLED)
        window["STOP"].update(disabled=True, button_color=BUTTON_DISABLED)
        window["LOGFILE"].update("Not Started")
        window["LAP"].update("N/A")
        window["TICK"].update("N/A")
        window["VEHICLE"].update("N/A")
        window["VENUE"].update("N/A")

# try and save the state
try:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)
except Exception as e:
    print(e)
    pass

# Finish up by removing from the screen
window.close()

