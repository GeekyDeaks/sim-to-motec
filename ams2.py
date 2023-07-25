import PySimpleGUI as sg
import json
import os
import time

from stm.version import __version__
from stm.ams2 import AMS2Logger, AMS2Sampler
from logging import getLogger, basicConfig, root, Handler, DEBUG

# try and load the sate
STATE_FILE = "ams2.cfg"

state = {
    "FREQ": "20",
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
    [sg.Text("Sampling Frequency")],
    [sg.Text("Imperial Units")],
    [sg.Text("Log File")],
    [sg.Text("Vehicle")],
    [sg.Text("Venue")],
    [sg.Text("Sequence")],
    [sg.Text("Game State")],
    [sg.Text("Race State")],
    [sg.Text("Session")],
    [sg.Text("Lap")],
]

values = [
    [sg.Input(state["FREQ"], key="FREQ", size=(5,1), enable_events=True), sg.Text("Hz", justification="l")],
    [sg.Checkbox("", state["IMPERIAL"], key="IMPERIAL", enable_events=True)],
    [sg.Text("Not Started",key="LOGFILE" )],
    [sg.Text("N/A", key="VEHICLE")],
    [sg.Text("N/A", key="VENUE")],
    [sg.Text("N/A", key="SEQ")],
    [sg.Text("N/A", key="GAMESTATE")],
    [sg.Text("N/A", key="RACESTATE")],
    [sg.Text("N/A", key="SESSION")],
    [sg.Text("N/A", key="LAP")],
]

# try and make the logs directory to check we have the correct permissions
canwrite = False
try:
    os.makedirs("logs", exist_ok=True)
    canwrite = True
except:
    labels.append([ sg.Text("ERROR", text_color="red")])
    values.append([ sg.Text("Cannot create logs directory, please copy ams2.exe to a writeable directory", text_color="red") ])

# Define the window's contents
layout = [
    [sg.Column(labels, element_justification='r'), sg.Column(values)],
    [
        sg.Button('Start', key="START", disabled=not canwrite), 
        sg.Button("Stop", key="STOP", disabled=True, button_color=BUTTON_DISABLED), 
        sg.Button('Quit', key="QUIT"),
        sg.Checkbox("Rawfile", key="RAWFILE")
     ],
    [sg.HorizontalSeparator()],
    [sg.Multiline(size=(100, 12), key="LOG", autoscroll=True, disabled=True)]     
]

# Create the window
window = sg.Window(f"AMS2 logger v{__version__}", layout, finalize=True)
# start the logger after creating the output element
basicConfig(
     level=DEBUG,
     format="%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s",
     datefmt="%H:%M:%S"
)

class LogHandler(Handler):

    def __init__(self):
        Handler.__init__(self)

    def emit(self, record):
        current = self.format(record) + "\n"
        window['LOG'].update(value=current, append=True)

handler = LogHandler()
handler.setFormatter(root.handlers[0].formatter)
root.addHandler(handler)
l = getLogger(__name__)

logger = None

# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read(timeout=500)
    # See if user wants to quit or window was closed
    if event in (sg.WINDOW_CLOSED, "QUIT"):
        break

    if event == "FREQ" and len(values['FREQ']) and values['FREQ'][-1] not in ('1234567890'):
        window["FREQ"].update(values['FREQ'][:-1])

    if event in state:
        state[event] = values[event]

    if event == "START":
        filetemplate = os.path.join("logs", "ams2", "{venue}_{vehicle}_{driver}_{session}_{datetime}")

        if values["RAWFILE"]:
            rawfile = os.path.join("logs", "raw", "ams2", f"{time.time():.0f}.db" )
        else:
            rawfile = None

        logger = AMS2Logger(
            rawfile=rawfile,
            sampler=AMS2Sampler(freq=values["FREQ"]),
            filetemplate=filetemplate,
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

            if p.driver:
                window["LAP"].update( f"{p.driver.mCurrentLap}/{p.mLapsInEvent}" )
            window["SEQ"].update(p.mSequenceNumber)
            window["VEHICLE"].update(logger.get_vehicle())
            window["VENUE"].update(logger.get_venue())
            window["GAMESTATE"].update(p.mGameState.name)
            window["RACESTATE"].update(p.mRaceState.name)
            window["SESSION"].update(p.mSessionState.name.title())
    else:
        window["QUIT"].update(disabled=False, button_color=BUTTON_ENABLED)
        window["START"].update(disabled=not canwrite, button_color=BUTTON_ENABLED)
        window["STOP"].update(disabled=True, button_color=BUTTON_DISABLED)
        window["LOGFILE"].update("Not Started")
        window["LAP"].update("N/A")
        window["SEQ"].update("N/A")
        window["VEHICLE"].update("N/A")
        window["VENUE"].update("N/A")
        window["GAMESTATE"].update("N/A")
        window["RACESTATE"].update("N/A")
        window["SESSION"].update("N/A")

# try and save the state
try:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)
except Exception as e:
    print(e)
    pass

# Finish up by removing from the screen
window.close()

