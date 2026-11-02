from tool_file.terminal_tools import run_command
from tool_file.info_tools import get_current_date, get_current_datetime, get_current_time, get_random_number
available_functions = {
    "run_command": run_command,
    "get_random_number": get_random_number,
    "get_current_time": get_current_time,
    "get_current_datetime": get_current_datetime,
    "get_current_date": get_current_date
}

tools = [
    run_command,
    get_current_date,
    get_current_datetime,
    get_current_time,
    get_random_number
]