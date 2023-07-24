"""LICENSE HEADER START

supervisor-shell-ui

A command-line interface clone of the built-in web interface provided by Supervisor for managing processes.

Copyright (C) 2023 Ciprian Mandache <https://ciprian.51k.eu>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

LICENSE HEADER STOP"""
from datetime import datetime

from . import common
from . import config
from . import screen
from . import keys

KEYBINDINGS_HELP = [
    "Esc: Exit Page",
    "Tab: Switch Section",
    "Enter: Execute",
    "PgUp/PgDn: Scroll Table",
    "Left/Right Arrow: Change Button",
    "Up/Down Arrow: Change Process"
]

KEYBINDINGS_HELP_SEPARATOR = " | "

exit = False
last_refresh_time = datetime.now()
selected_button = None
buttons = {}


def exit_page():
    global exit
    exit = True


def get_default_keybindings():
    return {
        keys.ESCAPE: exit_page,
        keys.ENTER: None,
        keys.TAB: None,
        keys.RIGHT: None,
        keys.LEFT: None,
        keys.PAGE_DOWN: None,
        keys.PAGE_UP: None,
        keys.UP: None,
        keys.DOWN: None
    }


keybindings = get_default_keybindings()


def refresh(fn):
    def wrapper(*args, **kwargs):
        global last_refresh_time
        screen.clear()
        last_refresh_time = datetime.now()

        return fn(*args, **kwargs)

    return wrapper


def get_selected_button_label():
    return buttons[selected_button]["label"]


def get_selected_button_action():
    return buttons[selected_button]["action"]


def cycle_button(direction=common.DIRECTION_RIGHT):
    global selected_button
    selected_button = (
        selected_button + common.get_movement_subtrahend(direction)) % len(buttons)


def set_keybinding(key, action, override_reserved=False):
    if key not in keybindings:
        raise Exception(f"key {key} is not supported")

    if not override_reserved:
        if key == keys.ESCAPE:
            raise Exception("keybinding for ESCAPE is reserved")

    if action is not None and not callable(action):
        raise Exception("action must be callable")

    keybindings[key] = action


def set_keybindings(keybindings, override_reserved=False):
    for key, action in keybindings.items():
        set_keybinding(key, action, override_reserved)


def handle_input():
    k = screen.getch()
    if k in keybindings and keybindings[k] is not None:
        keybindings[k]()


def draw_keybindings_help():
    lines = []
    line = ""
    max_len = 0

    def update_max_len(line):
        nonlocal max_len
        line_len = len(line)
        if line_len > max_len:
            max_len = line_len

    keybindings_help_separator_len = len(KEYBINDINGS_HELP_SEPARATOR)
    for item in KEYBINDINGS_HELP:
        if item != KEYBINDINGS_HELP[-1]:
            item += KEYBINDINGS_HELP_SEPARATOR

        if len(line) + len(item) + keybindings_help_separator_len > screen.width:
            line = line[:-keybindings_help_separator_len]
            update_max_len(line)
            lines.append(line)
            line = ""

        line += item

        if item == KEYBINDINGS_HELP[-1]:
            update_max_len(line)
            lines.append(line)

    if len(lines) == 1:
        screen.add_blank_line(screen.get_and_inc_current_draw_row_num())

    for line in lines:
        screen.addstr(screen.get_and_inc_current_draw_row_num(),
                      0, line.ljust(max_len), highlight=True)


def draw_title(title):
    title = f"{config.APP_TITLE} - {title} ({common.format_time(last_refresh_time)})"
    title_x = (screen.width - len(title)) // 2
    screen.addstr(screen.get_and_inc_current_draw_row_num(), title_x, title)


def draw_buttons(no_highlight=False):
    row = screen.get_and_inc_current_draw_row_num()
    start_pos = 0

    for button, props in buttons.items():
        label = props["label"]
        screen.addstr(row, start_pos, label, highlight=button ==
                      selected_button and not no_highlight)
        start_pos += len(label) + 2


def init(btns, selected_btn, kbindings=None, override_reserved_keybindings=False):
    global buttons, selected_button, exit
    buttons = btns
    selected_button = selected_btn
    exit = False

    set_keybindings(get_default_keybindings(), override_reserved=True)
    if kbindings is not None:
        set_keybindings(
            kbindings, override_reserved=override_reserved_keybindings)
