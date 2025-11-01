import os
from functions.config import MAX_CHARS
from google.genai import types

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads the content of a specified file, constrained to the working directory. Truncates if necessary.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The relative path of the file to read.",
            ),
        },
    ),
)

def get_file_content(working_directory, file_path):
    try:
        # Get absolute paths for safety
        abs_work_dir = os.path.abspath(working_directory)
        abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

        # 1. Ensure the file is inside the working directory
        if not abs_file_path.startswith(abs_work_dir):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        # 2. Ensure the file exists and is a regular file
        if not os.path.isfile(abs_file_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        # 3. Read the file safely
        with open(abs_file_path, "r", encoding="utf-8") as f:
            content = f.read(MAX_CHARS + 1)  # read slightly more to check if truncation needed

        # 4. Truncate if necessary
        if len(content) > MAX_CHARS:
            content = content[:MAX_CHARS] + f'[...]File "{file_path}" truncated at {MAX_CHARS} characters]'

        return content

    except Exception as e:
        return f"Error: {str(e)}"
