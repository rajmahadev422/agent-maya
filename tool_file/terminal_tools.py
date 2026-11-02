
import subprocess
import os

def run_command(command: str, directory: str = './') -> str:
    """
        Execute a CMD command in windows in the specified directory.
    """
    if directory == '' or not directory:
        directory = "./"
    
    try:
        if not os.path.isdir(directory):
            return "Error: Directory does not exist"

        process = subprocess.Popen(
            ["cmd.exe", "/c", command],
            cwd=directory
        )

        return f"Command started in visible CMD. PID: {process.pid}"

    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 60 seconds."
    
    except Exception as e:
        return f"Execution error: {e}"

    if not os.path.isdir(directory):
        return "Invalid directory"

    subprocess.Popen(
        ["cmd.exe", "/K"],
        cwd=directory,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

    return "User terminal opened."