import os
from google.genai import types

def get_file_content(working_directory, file_path):
    try:   
        working_directory = os.path.abspath(working_directory)
        absolute_path = os.path.abspath(os.path.join(working_directory, file_path))
        if os.path.commonpath([absolute_path, working_directory]) != working_directory:
            return (f"""Error: Cannot list "{file_path}" as it is outside the permitted working directory""")
        if not os.path.isfile(absolute_path):
            return (f'Error: File not found or is not a regular file: "{file_path}"')
        
        MAX_CHARS = 10000

        with open(absolute_path, "r", encoding="utf-8") as f:
            file_content_string = f.read(MAX_CHARS)
            extra = f.read(1)
        if extra:
            file_content_string += f'\n\n[...File "{file_path}" truncated at 10000 characters]'
        
        return file_content_string
    
    except OSError as e:
        return f"Error: {e}"
    

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Returns the first 10,000 characters of a document",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path of the file to read, relative to the working directory.",
            ),
        },

    ),
)
