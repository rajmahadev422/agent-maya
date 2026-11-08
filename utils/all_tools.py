import json
from config import MAYA_DIR
from tool_file.terminal_tools import (
    run_command,
    start_server,
    stop_server
)
from tool_file.info_tools import  (
    list_directory
)
from tool_file.file_tools import (
    read_file,
    write_file,
    update_file,
    delete_file,
    insert_file_text,
    replace_file_text,
    find_file_location
)
from tool_file.common_tools import (
    get_random_number,
    get_current_date,
    get_current_datetime,
    get_current_time,
    open_url_in_browser
)

schema_path = rf"{MAYA_DIR}/utils/tools_schema.json"
with open(schema_path, "r", encoding="utf-8") as file:
    tools = json.load(file)


available_functions = {}
for tool in tools:
  func_name = tool["function"]["name"]
  # Look up the function by name from the current global scope or module
  if func_name in globals():
    available_functions[func_name] = globals()[func_name]
  else:
    print(f"Warning: Tool function '{func_name}' is defined in JSON but not found in Python scope.")

print(f"Loaded {len(available_functions)} executable tools successfully. Done!")


# available_functions = {
#     "run_command": run_command,
#     "get_random_number": get_random_number,
#     "get_current_time": get_current_time,
#     "get_current_datetime": get_current_datetime,
#     "get_current_date": get_current_date,
#     "read_file": read_file,
#     "write_file": write_file,
#     "update_file": update_file,
#     "delete_file": delete_file,
#     "get_project_structure": list_directory,
#     "insert_file_text": insert_file_text,
#     "replace_file_text": replace_file_text,
#     "find_file_location": find_file_location
# }

# tools = [
#     run_command,
#     get_current_date,
#     get_current_datetime,
#     get_current_time,
#     get_random_number,
#     read_file,
#     write_file,
#     update_file,
#     delete_file,
#     list_directory,
#     insert_file_text,
#     replace_file_text
# ]
