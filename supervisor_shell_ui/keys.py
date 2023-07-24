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

ESCAPE = 27
ENTER = ord("\n")
TAB = ord('\t')
RIGHT = curses.KEY_RIGHT
LEFT = curses.KEY_LEFT
PAGE_DOWN = curses.KEY_NPAGE
PAGE_UP = curses.KEY_PPAGE
UP = curses.KEY_UP
DOWN = curses.KEY_DOWN
