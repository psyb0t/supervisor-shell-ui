#!/usr/bin/env python3
import sys
import glob

ARG_ADD = "add"
ARG_REMOVE = "remove"
ARG_UPDATE = "update"

SUPPORTED_ARGS = [ARG_ADD, ARG_REMOVE, ARG_UPDATE]

LICENSE_HEADER = """
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
"""

SOURCE_PATH = "./supervisor_shell_ui"


def _get_files():
    return glob.glob(f"{SOURCE_PATH}/**/*.py", recursive=True)


def _get_file_lines(file):
    with open(file, 'r') as f:
        return f.readlines()


def add():
    for file in _get_files():
        lines = _get_file_lines(file)
        if "\"\"\"LICENSE HEADER START" not in lines[0]:
            print(f"Adding license header to {file}")

            with open(file, 'w') as f:
                if lines[0].startswith("#!"):
                    f.write(lines[0])
                    lines = lines[1:]

                f.write("\"\"\"LICENSE HEADER START\n")
                f.write(LICENSE_HEADER)
                f.write("\nLICENSE HEADER STOP\"\"\"\n")
                f.writelines(lines)


def remove():
    for file in _get_files():
        print(f"Removing license header from {file}")

        lines = _get_file_lines(file)
        with open(file, 'w') as f:
            in_license = False
            for line in lines:
                if line.strip() == "\"\"\"LICENSE HEADER START":
                    in_license = True
                    continue

                if line.strip() == "LICENSE HEADER STOP\"\"\"":
                    in_license = False
                    continue

                if not in_license:
                    f.write(line)


def update():
    remove()
    add()


if __name__ == "__main__":

    if len(sys.argv) != 2 or sys.argv[1] not in SUPPORTED_ARGS:
        print(f"Usage: {sys.argv[0]} {SUPPORTED_ARGS}")
        sys.exit(1)

    arg = sys.argv[1]
    if arg == ARG_ADD:
        add()
    elif arg == ARG_REMOVE:
        remove()
    elif arg == ARG_UPDATE:
        update()
