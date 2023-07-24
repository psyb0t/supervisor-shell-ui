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

MIN_WIDTH = 110
MIN_HEIGHT = 20

stdscr = None
height = 0
width = 0
current_draw_row_num = 0


def __must_have_proper_dimensions():
    if width < MIN_WIDTH:
        raise Exception(
            f"screen width is {width} but the minimum is {MIN_WIDTH}")

    if height < MIN_HEIGHT:
        raise Exception(
            f"screen height is {height} but the minimum is {MIN_HEIGHT}")


def _must_have_proper_dimensions(fn):
    def wrapper(*args, **kwargs):
        __must_have_proper_dimensions()

        return fn(*args, **kwargs)

    return wrapper


def _must_have_stdscr(fn):
    def wrapper(*args, **kwargs):
        if stdscr is None:
            raise Exception("screen not initialized")

        return fn(*args, **kwargs)

    return wrapper


def init(scr):
    global stdscr, height, width
    stdscr = scr
    height, width = stdscr.getmaxyx()
    __must_have_proper_dimensions()
    curses.start_color()


def get_and_inc_current_draw_row_num():
    global current_draw_row_num
    draw_row_num = current_draw_row_num
    current_draw_row_num += 1
    if current_draw_row_num > height - 1:
        current_draw_row_num = height - 1

    return draw_row_num


def reset_current_draw_row_num():
    global current_draw_row_num
    current_draw_row_num = 0


@_must_have_stdscr
@_must_have_proper_dimensions
def handle_window_resize():
    global height, width
    if curses.is_term_resized(height, width):
        height, width = stdscr.getmaxyx()
        stdscr.clear()

        return True

    return False


@_must_have_stdscr
def addstr(row, start_pos, label, highlight=False):
    if highlight:
        stdscr.attron(curses.A_REVERSE)
        stdscr.addstr(row, start_pos, label)
        stdscr.attroff(curses.A_REVERSE)

        return

    stdscr.addstr(row, start_pos, label)


def add_blank_line(row):
    return addstr(row, 0, " " * width)


@_must_have_stdscr
def hline(*args, **kwargs):
    stdscr.hline(*args, **kwargs)


@_must_have_stdscr
def getch(*args, **kwargs):
    return stdscr.getch(*args, **kwargs)


@_must_have_stdscr
def refresh(*args, **kwargs):
    stdscr.refresh(*args, **kwargs)


@_must_have_stdscr
def clear(*args, **kwargs):
    stdscr.clear(*args, **kwargs)
