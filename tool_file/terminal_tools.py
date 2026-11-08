
import os
import subprocess
from config import PROJECT_DIR
from pathlib import Path

def run_command(command: str, directory: str = str(PROJECT_DIR)) -> str:
    """
    Execute a Windows CMD command in the current directory or given directory and return its actual output.

    """
    if not directory:
        directory = "./"

    try:
        if not os.path.isdir(directory):
            return "Error: Directory does not exist"

        process = subprocess.run(
            ["cmd.exe", "/c", command],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=60,
            encoding="utf-8",
            errors="replace"
        )

        output = process.stdout.strip()
        error = process.stderr.strip()

        result = []

        if output:
            result.append(output)

        if error:
            result.append(f"STDERR:\n{error}")

        if process.returncode != 0:
            result.append(f"Exit code: {process.returncode}")

        return "\n".join(result) if result else "Command executed successfully (no output)."

    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 60 seconds."

    except Exception as e:
        return f"Execution error: {e}"

# Global registry to track running background servers/processes
BACKGROUND_PROCESSES = {}
PROCESS_COUNTER = 0

def start_server(command: str, directory: str = "./") -> str:
    """
    Start a long-running process (like a dev server) in the background without blocking.
    
    Args:
        command: The shell command to run the server (e.g., 'node server.js', 'python -m http.server 8000').
        directory: The working directory where the server should run.
        
    Returns:
        A status message containing a process ID (proc_id) used to manage or stop the server later.
    """
    global PROCESS_COUNTER
    try:
        target_dir = Path(directory).resolve()
        if not target_dir.is_dir():
            return f"Error: Directory does not exist: {directory}"
        
        # Popen runs the process asynchronously in the background
        process = subprocess.Popen(
            ["cmd.exe", "/c", command],
            cwd=target_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        
        proc_id = f"proc_{PROCESS_COUNTER}"
        PROCESS_COUNTER += 1
        
        BACKGROUND_PROCESSES[proc_id] = {
            "process": process,
            "command": command,
            "directory": str(target_dir)
        }
        
        return f"Server/background process started successfully with ID '{proc_id}'. Command: '{command}' in '{target_dir}'."
    except Exception as e:
        return f"Error starting background process: {str(e)}"

def stop_server(proc_id: str) -> str:
    """
    Terminate a running background server or process by its ID.
    
    Args:
        proc_id: The process ID (e.g., 'proc_0') returned when starting the server.
        
    Returns:
        Status message.
    """
    if proc_id not in BACKGROUND_PROCESSES:
        return f"Error: Process ID '{proc_id}' not found."
    
    info = BACKGROUND_PROCESSES[proc_id]
    proc = info["process"]
    
    try:
        if proc.poll() is not None:
            return f"Process '{proc_id}' ({info['command']}) has already terminated."
        
        # Force kill the process tree on Windows to ensure child node processes are cleaned up
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
        return f"Successfully stopped background process '{proc_id}' ({info['command']})."
    except Exception as e:
        return f"Error terminating process: {str(e)}"