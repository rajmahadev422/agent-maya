
import os
import subprocess

def run_command(command: str, directory: str = './') -> str:
    """
    Execute a Windows CMD command and return its actual output.
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
