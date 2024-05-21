import os


def create_new_file_name(folder_path, file_name, fallback_extension, file_tag=None):
    if "." in file_name:
        file_name, _ = os.path.basename(file_name).split(".")

    file_tag = "" if file_tag is None else file_tag

    out_file = os.path.join(folder_path, f"{file_name}{file_tag}.{fallback_extension}")

    # do not overwrite existing files -> append (`number`) to the name instead
    i = 2
    while os.path.exists(out_file):
        out_file = os.path.join(
            folder_path, f"{file_name}{file_tag}({i}).{fallback_extension}"
        )
        i += 1

    return out_file
