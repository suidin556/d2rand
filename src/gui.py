import os
import subprocess
from collections import defaultdict

import PySimpleGUI as sg

from .options import options
from . import utils
from .randomize import do


groups = defaultdict(list)

def get_elems(options, parent_key=None, padding_left=0, parent_group=None):
    for option in options.values():
        key = option.name
        if parent_key:
            key = "{}__{}".format(parent_key, key)
        if option.required:
            o_elem = sg.Text(
                text=option.readable_name,
                tooltip=option.desc,
                # pad=((20,0),(10,0)),
            )
        else:   
            o_elem = sg.Checkbox(
                text=option.readable_name,
                default=option.enabled,
                enable_events=True,
                key=key,
                tooltip=option.desc,
                pad=((padding_left,0),(10,0)),
                metadata={"option":option}
            )
        if parent_group:
            group = parent_group
        else:
            group = option.group
        groups[group].append([o_elem])

        if option.type is range:
            groups[group].append([sg.Slider(
                range=(option.min, option.max),
                default_value=option.value,
                orientation="h",
                # enable_events=True,
                key="{}__value".format(key),
                pad=((padding_left+20,0),(0,0)),
                # visible=option.enabled
            )])
        elif option.type is int:
            groups[group].append([sg.InputText(
                default_text=option.value,
                # enable_events=True,
                key="{}__value".format(key),
                size=(15,1),
                pad=((padding_left+20,0),(0,0)),
                # visible=option.enabled
            )])
        elif option.type == "directory":
            groups[group].append([
                sg.Input(
                    visible=option.enabled,
                    default_text=option.value,
                    pad=((0,0),(0,0)),
                    # size=(35,1),
                    key="{}__value".format(key),
                ),
                sg.FolderBrowse(
                    # visible=option.enabled,
                    target="{}__value".format(key),
                )
            ])

        get_elems(option.options, key, padding_left+20, group)


sg.theme('SystemDefault')
# sg.theme('DarkTeal9')
# All the stuff inside your window.
layout = [[sg.Text("Hover over the settings to see more details.")]]

get_elems(options)


layout.append([
    sg.Column(
        layout=[
            [sg.Frame("Randomization Options", 
                layout=groups["random"],
                # pad=(10,10),
                # background_color="#f5f5f5",
            )],
            [sg.Frame("Other", 
                layout=groups["mode"],
                # pad=(10,10),
                # background_color="#f5f5f5",
            )],
        ],
        # pad=(10,10),
        # size=(300,150),
        # scrollable=True,
        # vertical_scroll_only=True,
    ),
    sg.Column(
        layout=[[
            sg.Frame("Adjust Values",
                layout=groups["adjust"],
                # pad=(10,10),
                # background_color="#f5f5f5",
            )
        ]],
        # pad=(10,10),
        # size=(300,150),
        # scrollable=True,
        # vertical_scroll_only=True,
    ),
])

layout += groups["other"]

randomize_btn = sg.Button(
    button_text="Randomize",
    key="RANDOMIZE",
    enable_events=True,
)


start_btn = sg.Button(
    button_text="Start D2",
    key="START_D2",
    enable_events=True,
)
layout.append([randomize_btn, start_btn] + utils.flatten(groups["start_options"]))

def start():
    window = sg.Window('D2 Randomizer', layout, resizable=True)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        # print(event, values)
        if event in (None, 'Cancel'):
            break
        if event == "RANDOMIZE":
            options.update_options(values)
            if options.DIABLO_PATH.value == "":
                sg.popup("Diablo Path can not be empty")
                continue
            try:
                do()
            except Exception as e:
                raise e
                print(e)
                sg.popup("There was an Error during randomization.")
            else:
                sg.popup("Randomization finished")
        elif event == "START_D2":
            d2path = values["DIABLO_PATH__value"]
            if not d2path:
                sg.popup("DIABLO_PATH needs to be set to start the game.")
                continue
            game_exe_path = os.path.join(d2path, "Diablo II.exe")
            if not os.path.isfile(game_exe_path):
                sg.popup("Diablo II.exe could not be found.")
                continue
            start_options = [game_exe_path, "-txt", "-direct"]
            if values["WINDOW_MODE"]:
                start_options.append("-w")
            with open(os.devnull, 'r+b', 0) as DEVNULL:
                p = subprocess.Popen(
                    start_options,
                    stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL, close_fds=True, cwd=d2path
                )



    window.close()









        # else:
        #     try:
        #         elem = window[event]
        #     except:
        #         continue
        #     val = values[event]
        #     if event == "DEBUG":
        #         window["-OUTPUT-"].update(visible=val)
            # if val is True or val is False:
            # for key in values.keys():
            #     if key.startswith("{}__".format(event)):
            #         if val is False:
            #             window[key].update(visible=val)
            #             window[key].hide_row()
            #         elif val is True:
            #             window[key].update(visible=val)
            #             window[key].unhide_row()
