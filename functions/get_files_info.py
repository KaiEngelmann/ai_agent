import os
from google.genai import types

def get_files_info(working_directory, directory="."):
    try:
        working_directory = os.path.abspath(working_directory)
        absolute_path = os.path.abspath(os.path.join(working_directory, directory))
        if os.path.commonpath([absolute_path, working_directory]) != working_directory:
            return (f"""Error: Cannot list "{directory}" as it is outside the permitted working directory""")
        if not os.path.isdir(absolute_path):
            return (f"""Error: "{directory}" is not a directory""")
        contents = os.listdir(absolute_path)
        file_list = []
        file_size = []
        is_dir = []
        for file in contents:
            full_path = os.path.join(absolute_path, file)
            file_list.append(file)
            file_size.append(os.path.getsize(full_path))
            is_dir.append(os.path.isdir(full_path))

        results = f"Result for {directory} directory:\n"
        for i in range(len(file_list)):
            name = file_list[i]
            size = file_size[i]
            is_directory = is_dir[i]
            results += f" - {name}: File_size={size}, is_dir={is_directory}\n"
        return results
    
    except OSError as e:
        return f"Error: {e}"
    
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





    
