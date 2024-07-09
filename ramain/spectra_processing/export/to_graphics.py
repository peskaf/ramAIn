import os
import numpy as np
from scipy import signal
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.gridspec import GridSpec


from ramain.utils.paths import create_new_file_name


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

    if not file_name:
        file_name = create_new_file_name(out_dir, in_file, file_format, file_tag)

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


# TODO: check
def export_stitched_maps_graphics(
    dataset: list,
    nmf_transformed: np.ndarray,
    nmf_components: np.ndarray,
    unified_x_axis: np.ndarray,
    file_name: str,
    in_files: list,
    out_dir: str = "",
) -> None:

    # cut the stitched map back into individual maps
    def get_individual_maps(dataset, nmf_transformed):
        maps = []
        start = 0
        for data in dataset:
            end = start + data.shape[0] * data.shape[1]
            maps.append(
                nmf_transformed[start:end, :].reshape(
                    (data.shape[0], data.shape[1], -1)
                )
            )
            start = end
        return maps

    N_COMPS = nmf_components.shape[0]

    dataset = [sm.data for sm in dataset]
    maps = get_individual_maps(dataset, nmf_transformed)

    MIN_COMPS = 8
    placeholders_to_add = max(MIN_COMPS - N_COMPS, 0)

    a4_width_in = 8.27
    a4_height_in = 11.69

    # make groups of max 5 maps
    maps_groups = [
        maps[i : i + 5] for i in range(0, len(maps), 5) if len(maps[i : i + 5]) > 0
    ]
    for k, maps_ in enumerate(maps_groups):
        pdf_filename = create_new_file_name(out_dir, file_name, "pdf", f"_{k + 1}")
        pdf = PdfPages(pdf_filename)
        # Create a figure
        fig = plt.figure(figsize=(a4_width_in, a4_height_in))

        # Define GridSpec
        gs = GridSpec(
            N_COMPS + placeholders_to_add,
            len(maps_) + 1,
            width_ratios=[1] * len(maps_) + [2],
        )

        # Add titles above each column
        for j in range(len(maps_)):
            ax = fig.add_subplot(gs[0, j])
            ax.set_title(f"File {j + 1}", fontsize=15)
            ax.axis("off")  # Hide axis for title cells

        # Set row labels and plot images
        for i in range(N_COMPS):
            ax = fig.add_subplot(gs[i, 0])
            ax.text(
                -0.2,
                0.5,
                f"{i + 1}",
                va="center",
                ha="right",
                fontsize=24,
                transform=ax.transAxes,
            )
            ax.axis("off")  # Hide axis for row label cells

            for j, map in enumerate(maps_):
                ax = fig.add_subplot(gs[i, j])
                img = map[:, :, i]
                ax.imshow(img)
                ax.axis("off")  # Hide axis for image cells

            ax = fig.add_subplot(gs[i, -1])
            ax.plot(unified_x_axis, nmf_components[i])
            ax.axis("off")  # Hide axis for component spectrum cells

        for i in range(placeholders_to_add):
            ax = fig.add_subplot(gs[N_COMPS + i, 0])
            ax.axis("off")  # Hide axis for placeholder cells
            for j, map in enumerate(maps_):
                ax = fig.add_subplot(gs[N_COMPS + i, j])
                # make img just white placeholder
                img = np.ones_like(map[:, :, 0])
                ax.imshow(img, cmap="gray_r")
                ax.axis("off")  # Hide axis for image cells
            ax = fig.add_subplot(gs[N_COMPS + i, -1])
            ax.axis("off")  # Hide axis for component spectrum cells

        plt.tight_layout()

        pdf.savefig()  # Save the current figure to the PDF
        pdf.close()

    # stats export ---------------------------------------------------------------------

    # Compute concentrations
    conc = [np.sum(map.reshape((-1, N_COMPS)), axis=0) for map in maps]

    # Concatenate all values for the respective component from all files
    pixel_conc = [
        np.concatenate([map[:, :, i].reshape(-1) for map in maps])
        for i in range(N_COMPS)
    ]

    # Bar plots PDF
    pdf_filename_bar = create_new_file_name(
        out_dir, file_name, "pdf", f"_concentration"
    )
    pdf_bar = PdfPages(pdf_filename_bar)
    a4_width_in = 11.69  # Landscape A4
    a4_height_in = 8.27

    # Create a figure for the bar plots and component plots
    fig_bar = plt.figure(figsize=(a4_width_in, a4_height_in))
    gs_bar = GridSpec(
        N_COMPS + placeholders_to_add, 3, width_ratios=[2, 2, 1]
    )  # Three columns: 1 for bar plot, 1 for component plot, 1 for histogram

    # Plot concentration bar plots, component plots, and histograms
    for i in range(N_COMPS):
        # Plot the bar plot for concentration
        ax_bar = fig_bar.add_subplot(gs_bar[i, 1])
        ax_bar.bar(list(range(len(dataset))), [c[i] for c in conc])
        ax_bar.set_xticks(list(range(len(dataset))))
        ax_bar.set_xticklabels(list(range(1, len(dataset) + 1)))
        if i == 0:
            ax_bar.set_title("Concentration in Individual Files")
        ax_bar.yaxis.set_label_position("right")
        ax_bar.set_ylabel("Total conc.", fontsize=8)
        ax_bar.ticklabel_format(
            axis="y", style="sci", scilimits=(0, 0)
        )  # Use scientific notation for y-axis labels

        # Plot the component plot
        ax_comp = fig_bar.add_subplot(gs_bar[i, 0])
        ax_comp.plot(unified_x_axis, nmf_components[i])
        if i == 0:
            ax_comp.set_title("Component Plot")
        ax_comp.set_ylabel("Intensity (a.u.)", fontsize=8)
        ax_comp.ticklabel_format(
            axis="y", style="sci", scilimits=(0, 0)
        )  # Use scientific notation for y-axis labels
        ax_comp.yaxis.set_label_position("right")

        # Plot the histogram of relative concentrations
        ax_hist = fig_bar.add_subplot(gs_bar[i, 2])
        hist, bins, _ = ax_hist.hist(
            pixel_conc[i], bins=int(np.ceil(1 + 3.3 * np.log10(len(dataset))))
        )  # number of bins according to the Sturges rule
        if i == 0:
            ax_hist.set_title("Concentration Frequency")
        ax_hist.set_ylabel("Frequency", fontsize=8)
        ax_hist.yaxis.set_label_position(
            "right"
        )  # Position the y-axis label on the right side
        ax_hist.ticklabel_format(
            axis="y", style="sci", scilimits=(0, 0)
        )  # Use scientific notation for y-axis labels

        # Add a common ylabel for all rows
        if i == 0:
            ax_hist.set_ylabel("Frequency")
            # ax_hist.yaxis.set_label_coords(1.2, 0.5)  # Adjust position for y-axis title

        if i == N_COMPS - 1:
            ax_bar.set_xlabel("File index")
            ax_hist.set_xlabel("Rel. concentration")
            ax_comp.set_xlabel("Raman shift (cm$^{-1}$)")

    for i in range(placeholders_to_add):
        ax_bar = fig_bar.add_subplot(gs_bar[N_COMPS + i, 1])
        ax_bar.axis("off")  # Hide axis for placeholder cells
        ax_comp = fig_bar.add_subplot(gs_bar[N_COMPS + i, 0])
        ax_comp.axis("off")  # Hide axis for placeholder cells
        ax_hist = fig_bar.add_subplot(gs_bar[N_COMPS + i, 2])
        ax_hist.axis("off")  # Hide axis for placeholder cells

    plt.tight_layout()
    plt.subplots_adjust(
        hspace=0.5, top=0.95, left=0.1, right=0.95, bottom=0.01
    )  # Adjust these values to minimize space

    pdf_bar.savefig(fig_bar)  # Save the bar plot and component figure to the PDF
    pdf_bar.close()

    # export graphics for each individual file -----------------------------------------
    outdir = out_dir + f"/individual_files_graphics_{file_name.split('.')[0]}"
    os.makedirs(
        outdir,
        exist_ok=True,
    )
    for map, data, in_file in zip(maps, dataset, in_files):

        export_components_graphics(
            data,
            unified_x_axis,
            [{"map": map[:, :, i], "plot": nmf_components[i]} for i in range(N_COMPS)],
            "png",
            in_file,
            out_dir=outdir,
        )

    # create text file that contains the file names and mapping to number (so order)
    with open(out_dir + "/file_mapping.txt", "w") as f:
        for i, in_file in enumerate(in_files):
            f.write(f"{i + 1}: {in_file}\n")
    # TODO: this is really not graphics, move this all to different file than this (i mean this whole function)

    # export components concentration to text in like text file in tab separated file
    with open(out_dir + "/concentration_export.txt", "w") as f:
        # in first column, I want the number of the file
        for i in range(len(dataset)):
            f.write(f"{i + 1}\t")
            # in the rest of the columns I want the relative concentration of the components, fix to 4 decimal places
            for j in range(N_COMPS):
                f.write(f"{conc[i][j]:.4f}\t")
            f.write("\n")

    # export txt components

    SEP = "\t"
    components_rows = np.array([nmf_components[i] for i in range(N_COMPS)])
    components_columns = components_rows.T
    data_columns = np.concatenate(
        (unified_x_axis[:, np.newaxis], components_columns), axis=1
    )

    with open(out_dir + "/components.txt", "w+") as f:
        for row in data_columns:
            for col_idx, column in enumerate(row):
                f.write(f"{column:.7e}")
                if col_idx < len(row) - 1:
                    f.write(SEP)
            f.write("\n")
