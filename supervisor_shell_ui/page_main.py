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
import time
import curses

from datetime import datetime
from . import common
from . import supervisor
from . import keys
from . import screen
from . import page
from . import page_tail

SECTION_HEADER = 0
SECTION_PROCESS_TABLE = 1


@page.refresh
def refresh():
    update_processes()


PAGE_TITLE = "Processes"

PAGE_BUTTON_REFRESH = 0
PAGE_BUTTON_RESTART_ALL = 1
PAGE_BUTTON_STOP_ALL = 2

PAGE_BUTTONS = {
    PAGE_BUTTON_REFRESH: common.get_button("Refresh", refresh),
    PAGE_BUTTON_RESTART_ALL: common.get_button("Restart All", supervisor.restart_all),
    PAGE_BUTTON_STOP_ALL: common.get_button("Stop All", supervisor.stop_all),
}

PROCESS_BUTTON_START = 0
PROCESS_BUTTON_RESTART = 1
PROCESS_BUTTON_STOP = 2
PROCESS_BUTTON_CLEAR_LOG = 3
PROCESS_BUTTON_TAIL_STDOUT = 4
PROCESS_BUTTON_TAIL_STDERR = 5

PROCESS_BUTTONS = {
    PROCESS_BUTTON_START: common.get_button("Start", supervisor.start_process),
    PROCESS_BUTTON_RESTART: common.get_button("Restart", supervisor.restart_process),
    PROCESS_BUTTON_STOP: common.get_button("Stop", supervisor.stop_process),
    PROCESS_BUTTON_CLEAR_LOG: common.get_button("Clear Log", supervisor.clear_process_log),
    PROCESS_BUTTON_TAIL_STDOUT: common.get_button("Tail Stdout"),
    PROCESS_BUTTON_TAIL_STDERR: common.get_button("Tail Stderr"),
}

PROCESS_STATE_RUNNING = "RUNNING"
PROCESS_STATE_STARTING = "STARTING"
PROCESS_STATE_STOPPED = "STOPPED"
PROCESS_STATE_BACKOFF = "BACKOFF"
PROCESS_STATE_EXITED = "EXITED"
PROCESS_STATE_FATAL = "FATAL"
PROCESS_STATE_UNKNOWN = "UNKNOWN"

PROCESS_STATE_TO_BUTTONS = {
    PROCESS_STATE_RUNNING: [
        PROCESS_BUTTON_RESTART,
        PROCESS_BUTTON_STOP,
        PROCESS_BUTTON_CLEAR_LOG,
        PROCESS_BUTTON_TAIL_STDOUT,
        PROCESS_BUTTON_TAIL_STDERR,
    ],
    PROCESS_STATE_STARTING: [
        PROCESS_BUTTON_STOP,
    ],
    PROCESS_STATE_STOPPED: [
        PROCESS_BUTTON_START,
        PROCESS_BUTTON_CLEAR_LOG,
    ],
    PROCESS_STATE_BACKOFF: [
        PROCESS_BUTTON_RESTART,
        PROCESS_BUTTON_STOP,
        PROCESS_BUTTON_CLEAR_LOG,
        PROCESS_BUTTON_TAIL_STDOUT,
        PROCESS_BUTTON_TAIL_STDERR,
    ],
    PROCESS_STATE_EXITED: [
        PROCESS_BUTTON_RESTART,
        PROCESS_BUTTON_STOP,
        PROCESS_BUTTON_CLEAR_LOG,
        PROCESS_BUTTON_TAIL_STDOUT,
        PROCESS_BUTTON_TAIL_STDERR,
    ],
    PROCESS_STATE_FATAL: [
        PROCESS_BUTTON_RESTART,
        PROCESS_BUTTON_STOP,
        PROCESS_BUTTON_CLEAR_LOG,
        PROCESS_BUTTON_TAIL_STDOUT,
        PROCESS_BUTTON_TAIL_STDERR,
    ],
    PROCESS_STATE_UNKNOWN: [
        PROCESS_BUTTON_RESTART,
        PROCESS_BUTTON_STOP,
        PROCESS_BUTTON_CLEAR_LOG,
        PROCESS_BUTTON_TAIL_STDOUT,
        PROCESS_BUTTON_TAIL_STDERR,
    ],
}

MAX_VISIBLE_PROCESS_BUTTONS_NUM = 5
PROCESS_TABLE_COLUMN_NAMES = ["State", "Description", "Name", "Action"]

STATUS_NUM_ROWS = 5

header_num_rows = 0
visible_processes_num = 0
process_table_scroll_offset = 0
selected_process_buttons = {}
selected_process_index = 0
current_section = SECTION_HEADER
processes = []
last_refresh_time = datetime.now()
last_action_output = ""
process_table_scroll_length = 5


def cycle_section():
    global current_section
    section_list = [SECTION_HEADER, SECTION_PROCESS_TABLE]
    current_section = section_list[(section_list.index(
        current_section) + 1) % len(section_list)]


def get_process_state_buttons(state):
    return PROCESS_STATE_TO_BUTTONS[state]


def get_process_button_label(button):
    return PROCESS_BUTTONS[button]["label"]


def get_process_button_action(button):
    return PROCESS_BUTTONS[button]["action"]


def get_selected_process_button():
    return selected_process_buttons[selected_process_index]


def get_selected_process_button_label():
    return get_process_button_label(selected_process_buttons[selected_process_index])


def get_selected_process_button_action():
    return get_process_button_action(selected_process_buttons[selected_process_index])


def get_selected_process_name():
    return processes[selected_process_index]["name"]


def get_selected_process_available_buttons():
    return get_process_available_buttons(selected_process_index)


def get_process_available_buttons(index):
    return get_process_state_buttons(processes[index]["state"])


def cycle_selected_process_button(direction=common.DIRECTION_RIGHT):
    available_buttons = get_selected_process_available_buttons()
    selected_process_button = get_selected_process_button()
    try:
        current_button_index = available_buttons.index(
            selected_process_button)
    except:
        current_button_index = 0

    selected_process_buttons[selected_process_index] = available_buttons[(
        current_button_index + common.get_movement_subtrahend(direction)) % len(available_buttons)]


def scroll_process_table_content(direction=common.DIRECTION_DOWN):
    global process_table_scroll_offset, selected_process_index
    if direction == common.DIRECTION_DOWN:
        process_table_scroll_offset += min(process_table_scroll_length, len(
            processes) - process_table_scroll_offset - visible_processes_num)
        selected_process_index = min(
            selected_process_index, process_table_scroll_offset + visible_processes_num - 1)
    elif direction == common.DIRECTION_UP:
        process_table_scroll_offset -= min(
            process_table_scroll_length, process_table_scroll_offset)
        selected_process_index = max(
            selected_process_index, process_table_scroll_offset)


def clear_all_lines():
    for i in range(screen.height):
        screen.addstr(i, 0, " " * (screen.width - 1))


def reset_selected_process_buttons():
    global selected_process_buttons
    for i, process in enumerate(processes):
        selected_process_buttons[i] = get_process_state_buttons(
            process["state"])[0]


def update_processes():
    global processes
    processes = supervisor.get_processes()
    reset_selected_process_buttons()


def cycle_process(direction=common.DIRECTION_DOWN):
    global process_table_scroll_offset, selected_process_index
    if current_section == SECTION_PROCESS_TABLE:
        reset_selected_process_buttons()

        if direction == common.DIRECTION_UP:
            selected_process_index = selected_process_index - \
                1 if selected_process_index > 0 else len(processes) - 1
        elif direction == common.DIRECTION_DOWN:
            selected_process_index = selected_process_index + \
                1 if selected_process_index < len(processes) - 1 else 0

        if selected_process_index < process_table_scroll_offset:
            process_table_scroll_offset = selected_process_index
        elif selected_process_index >= process_table_scroll_offset + visible_processes_num:
            process_table_scroll_offset = selected_process_index - visible_processes_num + 1


def handle_input_key_enter_section_header():
    global last_action_output
    action = page.get_selected_button_action()
    if action is None:
        return

    output = action()
    if output is not None:
        last_action_output = output

    refresh()


def handle_input_key_enter_section_table():
    global last_action_output
    selected_process_button = get_selected_process_button()
    process_name = get_selected_process_name()
    if selected_process_button in [PROCESS_BUTTON_TAIL_STDOUT, PROCESS_BUTTON_TAIL_STDERR]:
        log_source = supervisor.LOG_SOURCE_STDOUT
        if selected_process_button == PROCESS_BUTTON_TAIL_STDERR:
            log_source = supervisor.LOG_SOURCE_STDERR

        page_tail.enter(process_name, log_source)
        init()
    else:
        action = get_selected_process_button_action()
        if action is None:
            return

        last_action_output = action(process_name)

    refresh()


def handle_input_key_enter():
    if current_section == SECTION_HEADER:
        handle_input_key_enter_section_header()
    elif current_section == SECTION_PROCESS_TABLE:
        handle_input_key_enter_section_table()


def handle_input_key_right():
    if current_section == SECTION_HEADER:
        page.cycle_button()
    elif current_section == SECTION_PROCESS_TABLE:
        cycle_selected_process_button()


def handle_input_key_left():
    if current_section == SECTION_HEADER:
        page.cycle_button(common.DIRECTION_LEFT)
    elif current_section == SECTION_PROCESS_TABLE:
        cycle_selected_process_button(common.DIRECTION_LEFT)


def handle_input_key_page_down():
    scroll_process_table_content()


def handle_input_key_page_up():
    scroll_process_table_content(common.DIRECTION_UP)


def handle_input_key_down():
    global process_table_scroll_offset, selected_process_index
    if current_section == SECTION_PROCESS_TABLE:
        cycle_process()


def handle_input_key_up():
    global process_table_scroll_offset, selected_process_index
    if current_section == SECTION_PROCESS_TABLE:
        cycle_process(common.DIRECTION_UP)


def handle_input_key_tab():
    cycle_section()


def draw_process_table_row(process_table_content_start_row, process_index):
    row = screen.get_and_inc_current_draw_row_num()
    table_columns_num = len(PROCESS_TABLE_COLUMN_NAMES) + \
        MAX_VISIBLE_PROCESS_BUTTONS_NUM // 2
    process = processes[process_index]
    state, description, name = process["state"], process["description"], process["name"]
    column_width = max(10, screen.width // table_columns_num)
    process_details = "{:<{}}{:<{}}{:<{}}".format(
        common.truncate_string(state, column_width),
        column_width,
        common.truncate_string(description, column_width),
        column_width,
        common.truncate_string(name, column_width),
        column_width,
    )

    row_in_visible_table = row - process_table_content_start_row
    selected_process_in_visible_table = selected_process_index - \
        process_table_scroll_offset

    is_selected_process = current_section == SECTION_PROCESS_TABLE and \
        row_in_visible_table == selected_process_in_visible_table

    screen.addstr(row, 0, process_details, highlight=is_selected_process)

    start_pos = len(process_details)

    selected_process_button = selected_process_buttons[selected_process_index]
    available_buttons = get_process_available_buttons(process_index)
    for button in available_buttons:
        button_label = get_process_button_label(button)
        screen.addstr(row, start_pos, button_label,
                      highlight=is_selected_process and button == selected_process_button)
        start_pos += len(button_label) + 2


def draw_process_table_columns():
    row = screen.get_and_inc_current_draw_row_num()

    table_columns_num = len(PROCESS_TABLE_COLUMN_NAMES) + \
        MAX_VISIBLE_PROCESS_BUTTONS_NUM // 2

    start_pos = 0
    column_width = screen.width // table_columns_num
    for name in PROCESS_TABLE_COLUMN_NAMES:
        screen.addstr(row, start_pos, "{:<{}}".format(
            name, column_width))
        start_pos += column_width


def draw_process_table_content():
    if len(processes) > 0:
        display_processes = processes[process_table_scroll_offset:
                                      process_table_scroll_offset + visible_processes_num]
        process_table_content_start_row = screen.current_draw_row_num
        for i, _ in enumerate(display_processes):
            draw_process_table_row(
                process_table_content_start_row, i + process_table_scroll_offset)
    else:
        no_processes_message = "No Processes"
        message_x = (screen.width - len(no_processes_message)) // 2
        screen.addstr(screen.get_and_inc_current_draw_row_num(),
                      message_x, no_processes_message)

    displayed_lines = len(display_processes) if len(processes) > 0 else 1
    remaining_lines = visible_processes_num - displayed_lines
    for _ in range(remaining_lines):
        screen.addstr(screen.get_and_inc_current_draw_row_num(), 0, "")



def draw_process_table():
    global visible_processes_num, process_table_scroll_length
    draw_process_table_columns()

    screen.hline(screen.get_and_inc_current_draw_row_num(),
                 0, curses.ACS_HLINE, screen.width)

    visible_processes_num = screen.height
    # subtract the header rows
    visible_processes_num -= header_num_rows
    # subtract the status delimiter line row
    visible_processes_num -= 1
    # subtract the status rows
    visible_processes_num -= STATUS_NUM_ROWS
    # subtract the table columns row
    visible_processes_num -= 1
    # subtract the delimiter line rows before the table content
    visible_processes_num -= 1
    # subtract the keybindings help rows
    visible_processes_num -= 2

    process_table_scroll_length = visible_processes_num // 4
    draw_process_table_content()


def clear_status():
    status_start_num_row = screen.height - STATUS_NUM_ROWS
    for i in range(STATUS_NUM_ROWS):
        if status_start_num_row + i < screen.height:
            screen.addstr(status_start_num_row + i,
                          0, " " * (screen.width - 1))


def draw_status():
    screen.hline(screen.get_and_inc_current_draw_row_num(),
                 0, curses.ACS_HLINE, screen.width)

    clear_status()
    status_lines = [""] * STATUS_NUM_ROWS
    for i, line in enumerate(last_action_output.strip().split('\n')[-STATUS_NUM_ROWS:]):
        status_lines[i] = line.strip()

    for line in status_lines:
        screen.addstr(screen.get_and_inc_current_draw_row_num(), 0, line)


def draw_header():
    global header_num_rows
    start_draw_row_num = screen.current_draw_row_num

    page.draw_title(PAGE_TITLE)
    page.draw_buttons(current_section != SECTION_HEADER)
    screen.add_blank_line(screen.get_and_inc_current_draw_row_num())

    header_num_rows = screen.current_draw_row_num - start_draw_row_num


def draw():
    screen.reset_current_draw_row_num()

    draw_header()
    draw_process_table()
    draw_status()
    page.draw_keybindings_help()

    screen.refresh()


KEYBINDINGS = {
    keys.RIGHT: handle_input_key_right,
    keys.LEFT: handle_input_key_left,
    keys.PAGE_DOWN: handle_input_key_page_down,
    keys.PAGE_UP: handle_input_key_page_up,
    keys.UP: handle_input_key_up,
    keys.DOWN: handle_input_key_down,
    keys.TAB: handle_input_key_tab,
    keys.ENTER: handle_input_key_enter,
}


def init():
    page.init(PAGE_BUTTONS, PAGE_BUTTON_REFRESH, KEYBINDINGS)


def enter():
    init()
    refresh()

    last_process_table_scroll_offset = process_table_scroll_offset
    while not page.exit:
        screen.handle_window_resize()

        if last_process_table_scroll_offset != process_table_scroll_offset:
            screen.clear()
            last_process_table_scroll_offset = process_table_scroll_offset

        draw()
        page.handle_input()
        time.sleep(0.01)
