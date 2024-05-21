import numpy as np
import os


def export_components_txt(
    components: list,
    x_axis: np.ndarray,
    in_file: str,
    out_dir: str = "",
    file_name: str = "",
    file_tag: str = "",
) -> None:
    """
    A function for components exporting into txt files.

    Parameters:
        file_name (str): Name of the file where the output should be stored.
    """

    if len(components) == 0:
        raise Exception("components have not been made yet.")

    file_format = "txt"

    if not file_name and out_dir:
        # construct the file name
        file_name = os.path.basename(file_name)
        if "." in file_name:
            file_name, _ = os.path.basename(file_name).split(".")
        out_file = os.path.join(out_dir, file_name + file_tag + "." + file_format)

        # do not overwrite on auto export -> apend ('number') to the file name instead
        if os.path.exists(out_file):
            i = 2
            out_file = os.path.join(
                out_dir, file_name + file_tag + f"({i})" + "." + file_format
            )
            while os.path.exists(out_file):
                i += 1
                out_file = os.path.join(
                    out_dir, file_name + file_tag + f"({i})" + "." + file_format
                )
        file_name = out_file
    else:
        file_name = os.path.basename(file_name)
        if "." in file_name:
            file_name, _ = os.path.basename(file_name).split(".")
        file_name = os.path.join(out_dir, file_name + file_tag + "." + file_format)

    SEP = "\t"
    components_rows = np.array([component["plot"] for component in components])
    components_columns = components_rows.T
    data_columns = np.concatenate((x_axis[:, np.newaxis], components_columns), axis=1)

    with open(file_name, "w+") as f:
        for row in data_columns:
            for col_idx, column in enumerate(row):
                f.write(f"{column:.7e}")
                if col_idx < len(row) - 1:
                    f.write(SEP)
            f.write("\n")
