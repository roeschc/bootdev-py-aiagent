import os
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

def get_files_info(working_directory, directory="."):
    try:
        full_path = os.path.join(working_directory, directory)

        abs_working_directory = os.path.abspath(working_directory)
        abs_target_directory = os.path.abspath(full_path)

        if not abs_target_directory.startswith(abs_working_directory):
            return f"Error: Cannot list {directory}. as it is outside the permitted working directory"
        
        if not os.path.isdir(abs_target_directory):
            return f"Error: {directory} is not a directory."
        
        items = os.listdir(abs_target_directory)
        lines = []

        for item in items:
            item_path = os.path.join(abs_target_directory, item)
            is_dir = os.path.isdir(item_path)

            try:
                size = os.path.getsize(item_path)
            except Exception as e:
                size = f"Error retrieving size: {e}"
            
            lines.append(f"- {item}: file_size={size} bytes, is_dir={is_dir}")

        return "\n".join(lines)
    except Exception as e:
        return f"Error: {str(e)}"