import os
from google.genai import types

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes or overwrites content to a specified file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The relative path of the file to write to.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.",
            ),
        },
    ),
)

def write_file(working_directory, file_path, content):
    try:
        
        abs_work_dir = os.path.abspath(working_directory)
        abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

        
        if not abs_file_path.startswith(abs_work_dir):
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        
        dir_name = os.path.dirname(abs_file_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        
        with open(abs_file_path, "w", encoding="utf-8") as f:
            f.write(content)

        
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

    except Exception as e:
        return f"Error: {str(e)}"
