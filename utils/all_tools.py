from tool_file.terminal_tools import run_command
from tool_file.info_tools import get_current_date, get_current_datetime, get_current_time, get_random_number
from tool_file.file_tools import read_file, write_file, update_file, delete_file

available_functions = {
    "run_command": run_command,
    "get_random_number": get_random_number,
    "get_current_time": get_current_time,
    "get_current_datetime": get_current_datetime,
    "get_current_date": get_current_date,
    "read_file": read_file,
    "write_file": write_file,
    "update_file": update_file,
    "delete_file": delete_file
}

tools = [
    run_command,
    get_current_date,
    get_current_datetime,
    get_current_time,
    get_random_number,
    read_file,
    write_file,
    update_file,
    delete_file
]
