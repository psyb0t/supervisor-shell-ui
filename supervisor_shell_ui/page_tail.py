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
import curses
import time
import textwrap

from . import common
from . import keys
from . import supervisor
from . import screen
from . import page

PAGE_TITLE = "Tail"
PAGE_BUTTON_REFRESH = 0


@page.refresh
def refresh():
    update_process_log()


PAGE_BUTTONS = {
    PAGE_BUTTON_REFRESH: {
        "label": "Refresh",
        "action": refresh,
    },
}

process_name = ""
log_source = ""
last_action_output = ""
process_name = ""
log_source = ""


def update_process_log():
    global last_action_output
    byte_count = (screen.height) * screen.width
    last_action_output = supervisor.tail_process_log(
        process_name, log_source, byte_count)


def handle_input_key_enter():
    action = page.get_selected_button_action()
    if action is None:
        return

    action()


def handle_input_key_right():
    page.cycle_button()


def handle_input_key_left():
    page.cycle_button(common.DIRECTION_LEFT)


def draw_process_log():
    output_lines = last_action_output.split('\n')
    formatted_output_lines = []
    for line in output_lines:
        formatted_output_lines.extend(
            textwrap.wrap(line, screen.width - 1))

    visible_lines_num = screen.height - screen.current_draw_row_num
    # subtract the keybindings help rows
    visible_lines_num -= 2

    start_index = max(0, len(formatted_output_lines) - visible_lines_num)
    truncated_formatted_output_lines = formatted_output_lines[start_index:]

    while len(truncated_formatted_output_lines) < visible_lines_num:
        truncated_formatted_output_lines.append("")

    for line in truncated_formatted_output_lines:
        screen.addstr(
            screen.get_and_inc_current_draw_row_num(), 0, line)


def draw_header():
    page.draw_title(f"{PAGE_TITLE} {process_name} {log_source}")
    page.draw_buttons()


def draw():
    screen.reset_current_draw_row_num()
    draw_header()

    screen.hline(screen.get_and_inc_current_draw_row_num(),
                 0, curses.ACS_HLINE, screen.width)

    draw_process_log()
    page.draw_keybindings_help()
    screen.refresh()


KEYBINDINGS = {
    keys.RIGHT: handle_input_key_right,
    keys.LEFT: handle_input_key_left,
    keys.ENTER: handle_input_key_enter,
}


def init():
    page.init(PAGE_BUTTONS, PAGE_BUTTON_REFRESH, KEYBINDINGS)


def enter(pname, logsrc):
    global process_name, log_source
    process_name = pname
    log_source = logsrc

    init()
    refresh()

    while not page.exit:
        if screen.handle_window_resize():
            refresh()

        draw()
        page.handle_input()
        time.sleep(0.01)
