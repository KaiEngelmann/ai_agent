import os
import subprocess

def run_python_file(working_directory, file_path, args=None):
    if args is None:
        args = []
    try:
        working_directory = os.path.abspath(working_directory)
        absolute_path = os.path.abspath(os.path.join(working_directory, file_path))
        if os.path.commonpath([absolute_path, working_directory]) != working_directory:
            return (f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory')
        if not os.path.exists(absolute_path):
            return (f'Error: File "{file_path}" not found.')
        file_name = os.path.basename(absolute_path)
        if not file_name.endswith(".py"):
            return (f'Error: "{file_path}" is not a Python file.')
        command = ['python', absolute_path] + args
        result = subprocess.run(
        command,
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            return (f"Process exited with code {result.returncode}")
        if result.stdout:
            return (f"STDOUT:\n{result.stdout}\n STDERR:\n{result.stderr}")
        else:
            return ("No output produced")
        
    except subprocess.TimeoutExpired as e:
        return f"Error: executing Python file: {e}"
    except OSError as e:
        return f"Error: executing Python file: {e}"
    except Exception as e:
        return f"Error: executing Python file: {e}"
