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
import requests_unixsocket
import xml.etree.ElementTree as ET
import socket
from urllib.parse import quote
from supervisor_shell_ui import config

session = requests_unixsocket.Session()

LOG_SOURCE_STDOUT = "stdout"
LOG_SOURCE_STDERR = "stderr"


def socket_exists(sock_path):
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(sock_path)
        client.close()
        return True
    except Exception as e:
        print(f"Couldn't connect to socket: {e}")
        return False


def exec_rpc(method_name, *params):
    if not socket_exists(config.SUPERVISOR_SOCK_PATH):
        raise Exception(
            f"Supervisor socket not found: {config.SUPERVISOR_SOCK_PATH}")

    param_str = "".join(
        [f"<param><value><string>{p}</string></value></param>" for p in params])

    data = f"""<?xml version="1.0"?>
<methodCall>
    <methodName>{method_name}</methodName>
    <params>
        {param_str}
    </params>
</methodCall>
"""

    url = f'http+unix://{quote(config.SUPERVISOR_SOCK_PATH, safe="")}/RPC2'
    resp = session.post(url, data=data)
    if resp.status_code != 200:
        raise Exception(f"RPC call failed: {resp.text}")

    return resp.text


def parse_process_info(struct_element):
    process = {}
    for member in struct_element.findall("member"):
        name = member.find("name").text
        value_type = list(member.find("value"))[0].tag
        val = member.find(f"value/{value_type}").text
        process[name] = int(val) if value_type == "int" else val

    process["state"] = process["statename"]

    return process


def parse_process_list_info(xml_data):
    processes = []
    for value in xml_data.findall(".//array/data/value/struct"):
        process = parse_process_info(value)
        processes.append(process)

    return processes


def get_processes():
    raw_data = exec_rpc("supervisor.getAllProcessInfo")
    root = ET.fromstring(raw_data)
    processes = parse_process_list_info(root)
    processes = sorted(processes, key=lambda process: process["name"])

    return processes


def get_process(name):
    raw_data = exec_rpc("supervisor.getProcessInfo", name)
    root = ET.fromstring(raw_data)
    process = parse_process_info(root.find(".//struct"))

    return process


def tail_process_log(name, log_source, byte_count):
    rpc_method = "supervisor.tailProcessStdoutLog"
    if log_source == LOG_SOURCE_STDERR:
        rpc_method = "supervisor.tailProcessStderrLog"

    raw_data = exec_rpc(rpc_method, name, 0, byte_count)
    root = ET.fromstring(raw_data)
    log_data = root.find(".//array/data/value/string").text

    if log_data is None:
        raise Exception(f'Process {name} has no {log_source} log')

    return log_data


def restart_all():
    processes = get_processes()
    for process in processes:
        restart_process(process["name"])

    return "Restarted all processes."


def stop_all():
    exec_rpc("supervisor.stopAllProcesses")

    return "Stopped all processes."


def start_process(name):
    exec_rpc("supervisor.startProcess", name)

    return f"Started process {name}."


def stop_process(name):
    exec_rpc("supervisor.stopProcess", name)

    return f"Stopped process {name}."


def restart_process(name):
    stop_process(name)
    start_process(name)

    return f"Restarted process {name}."


def clear_process_log(name):
    exec_rpc("supervisor.clearProcessLogs", name)

    return f"Cleared logs for process {name}."
