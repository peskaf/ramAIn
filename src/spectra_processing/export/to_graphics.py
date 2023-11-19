import os
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as patches


def export_components_graphics(
    spectral_map: np.ndarray,
    x_axis: np.ndarray,
    components: list,
    file_format: str,
    in_file: str,
    cmap: str = "viridis",
    out_dir: str = "",
    file_name: str = "",
    file_tag: str = "",
) -> None:
    """
    A function for components exporting for publications.

    Parameters:
        file_name (str): Name of the file where the output should be stored.
        file_format (str): Format of the output, possible formats: png, pdf, ps, eps, svg.
    """

    if len(components) == 0:
        raise Exception("components have not been made yet.")

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

    # matplotlib pic export
    n_components = len(components)

    # letters for components identification
    comp_letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]

    # reverse ([::-1]) -> want the best components on the top and plotting happens from the bottom
    component_plots = [component["plot"] for component in components][::-1]
    component_maps = [component["map"] for component in components][::-1]

    plt.figure(figsize=(14, n_components * 2.5), clear=True)

    # set white background on exported images
    plt.rcParams["savefig.facecolor"] = "white"

    # colors for matplotlib plotting
    colors = list(mcolors.TABLEAU_COLORS)
    # subplot params
    n_rows = len(component_plots)
    n_cols = 2
    index = 1

    # maps
    for i in range(n_components):
        ax = plt.subplot(n_rows, n_cols, index)
        plt.axis("off")
        # set limist so that frame can be made
        ax.set_xlim(-1.5, spectral_map.shape[0] + 1.5)
        ax.set_ylim(-1.5, spectral_map.shape[1] + 1.5)

        # frame with color corresponding to plot's one
        rec = patches.Rectangle(
            (-1.5, -1.5),
            spectral_map.shape[0] + 3,
            spectral_map.shape[1] + 3,
            linewidth=2,
            edgecolor=colors[n_components - 1 - i],
            facecolor=colors[n_components - 1 - i],
        )
        rec.set_zorder(0)
        ax.add_patch(rec)

        # need to plot starting from the last image so that position fits with plot
        plt.imshow(
            component_maps[n_components - 1 - i]
            .reshape(spectral_map.shape[0], spectral_map.shape[1])
            .T,
            extent=[0, spectral_map.shape[0], 0, spectral_map.shape[1]],
            cmap=cmap,
        )

        # move to next row
        index += n_cols

    # plots

    # shifts for annotation and lines so that they can be on top of each other in one plot
    shift_step = np.max(component_plots) + 3

    letter_shift_x = -150
    letter_shift_y = -5
    annotaion_shift_y = 0.6
    annotation_shift_x = -0.015 * len(x_axis)
    shift = 0

    plt.subplot(n_components, 2, (2, 2 * n_components))

    # set ylim so that upper plot has same space above as other plots
    plt.ylim(top=shift_step * n_components, bottom=-1)
    plt.xlim(x_axis[0], x_axis[-1])
    plt.axis("on")

    for i in range(n_components):
        plt.plot(x_axis, component_plots[i] + shift, linewidth=2, color=colors[i])

        # find and annotate important peaks
        peaks, _ = signal.find_peaks(component_plots[i], prominence=0.8, distance=20)
        for peak_index in peaks:
            plt.annotate(
                f"{int(np.round(x_axis[peak_index]))}",
                (
                    x_axis[peak_index] + annotation_shift_x,
                    component_plots[i][peak_index] + shift + annotaion_shift_y,
                ),
                ha="left",
                rotation=90,
            )

        # letter annotation
        plt.annotate(
            comp_letters[n_components - 1 - i],
            (
                x_axis[-1] + letter_shift_x,
                (i + 1) * shift_step + letter_shift_y,
            ),
            size="xx-large",
            weight="bold",
        )
        shift += shift_step

    # reduce space between maps and plots
    # plt.subplots_adjust(wspace=-0.2, hspace=0.1)

    plt.xlabel("Raman shift (cm$^{-1}$)")
    plt.ylabel("Intensity (a.u.)")
    plt.yticks([])

    plt.tight_layout()
    plt.savefig(file_name, bbox_inches="tight", format=file_format)
    # close the figure as this may not run in the main thread
    plt.close()
