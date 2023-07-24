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
import subprocess

LOG_SOURCE_STDOUT = "stdout"
LOG_SOURCE_STDERR = "stderr"


def exec(command, *args):
    command_args = ['supervisorctl', command] + list(args)
    try:
        output = subprocess.check_output(
            command_args, stderr=subprocess.STDOUT).decode('utf-8')
    except subprocess.CalledProcessError as e:
        output = e.output.decode('utf-8')

    return output.strip()


def get_processes():
    try:
        output = exec('status')
    except subprocess.CalledProcessError as e:
        output = e.output.decode('utf-8')
        exit_status = e.returncode
        if exit_status != 3:
            raise Exception(f"Unexpected exit status: {exit_status}")

    lines = output.strip().split('\n')
    processes = []
    for line in lines:
        parts = line.split()
        state = parts[1]
        description = ' '.join(parts[2:]).replace(',', ' ')
        name = parts[0]

        processes.append({
            "state": state,
            "description": description,
            "name": name,
        })

    processes = sorted(processes, key=lambda process: process["name"])

    return processes


def tail_process_log(process_name, log_source, byte_count):
    return exec('tail', f'-{byte_count}', process_name, log_source)


def restart_all():
    return exec('restart', 'all')


def stop_all():
    return exec('stop', 'all')


def start_process(process_name):
    return exec('start', process_name)


def restart_process(process_name):
    return exec('restart', process_name)


def stop_process(process_name):
    return exec('stop', process_name)


def clear_process_log(process_name):
    return exec('clear', process_name)
