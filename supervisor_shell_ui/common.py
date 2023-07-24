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
DIRECTION_RIGHT = 0
DIRECTION_LEFT = 1
DIRECTION_UP = 2
DIRECTION_DOWN = 3


def get_movement_subtrahend(direction):
    if direction == DIRECTION_RIGHT:
        return 1
    elif direction == DIRECTION_LEFT:
        return -1

    return 0


def truncate_string(string, length):
    if len(string) > length:
        return string[:length - 3] + '...'

    return string


def format_time(t):
    return t.strftime('%A %d %B %Y %H:%M:%S')


def get_button(label, action=lambda: None):
    return {
        "label": label,
        "action": action,
    }
