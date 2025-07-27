import os

def write_file(working_directory, file_path, content):
    try:
        working_directory = os.path.abspath(working_directory)
        absolute_path = os.path.abspath(os.path.join(working_directory, file_path))
        if os.path.commonpath([absolute_path, working_directory]) != working_directory:
            return (f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory')
        dir_name = os.path.dirname(absolute_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        with open(absolute_path, "w") as f:
            f.write(content)
        return (f'Successfully wrote to "{file_path}" ({len(content)} characters written)')
        
    except OSError as e:
        return f"Error: {e}"
