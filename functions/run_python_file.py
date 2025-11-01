import os
import subprocess
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file with optional arguments, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The relative path of the Python file to run.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Optional list of arguments to pass to the Python script.",
                items=types.Schema(type=types.Type.STRING)
            ),
        },
    ),
)

def run_python_file(working_directory, file_path, args=[]):
    try:
        
        abs_work_dir = os.path.abspath(working_directory)
        abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

        
        if not abs_file_path.startswith(abs_work_dir):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        
        if not os.path.exists(abs_file_path):
            return f'Error: File "{file_path}" not found.'

        
        if not abs_file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file.'

        
        completed = subprocess.run(
            ["python3", abs_file_path, *args],
            capture_output=True,
            text=True,
            cwd=abs_work_dir,
            timeout=30
        )

        
        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()

        output_parts = []
        if stdout:
            output_parts.append(f"STDOUT:\n{stdout}")
        if stderr:
            output_parts.append(f"STDERR:\n{stderr}")
        if completed.returncode != 0:
            output_parts.append(f"Process exited with code {completed.returncode}")

        
        if not output_parts:
            return "No output produced."

        return "\n".join(output_parts)

    except Exception as e:
        return f"Error: executing Python file: {e}"
