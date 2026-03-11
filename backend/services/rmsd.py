import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from matplotlib.gridspec import GridSpec
import os

# --------------------------------------------------
# Configuración global
# --------------------------------------------------
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

# COLOR_PALETTE = [
#     "#000000", "#8d25a7", "#d141c7", "#e170c0", "#c52a91", 
#     "#a70e62", "#85113d", "#630f5b", "#541191", "#4915be", 
#     "#101167", "#2d3280", "#2357d5", "#5b98f4", "#5892be", 
#     "#6ecad5", "#207b7d", "#2b8753", "#5ba349", "#8ed73d", 
#     "#bbde01", "#f0c53a", "#d48d08", "#8a4032", "#fc843a", 
#     "#f25829", "#e00233", "#455894"
# ]
COLOR_PALETTE = [
    "#000000", "#e170c0", "#c52a91"
]
# --------------------------------------------------
# Leer XVG
# --------------------------------------------------
def read_xvg(file):
    data = []
    with open(file) as f:
        for line in f:
            if line.startswith(("#", "@")):
                continue
            data.append([float(x) for x in line.split()])
    return np.array(data)

def get_label_from_filename(filepath):
    basename = os.path.basename(filepath)
    return basename.replace("-rmsd.xvg", "")

# --------------------------------------------------
# Plot RMSD
# --------------------------------------------------
def plot_rmsd(input_files, output_file):

    if isinstance(input_files, str):
        input_files = [input_files]

    all_data = []
    max_time = 0
    max_rmsd = 0

    for file in input_files:
        data = read_xvg(file)
        all_data.append(data)
        max_time = max(max_time, data[:, 0].max())
        max_rmsd = max(max_rmsd, data[:, 1].max())

    fig = plt.figure(figsize=(14, 6))
    gs = GridSpec(1, 2, width_ratios=[7, 3])

    ax_rmsd = fig.add_subplot(gs[0])
    ax_pdf = fig.add_subplot(gs[1], sharey=ax_rmsd)

    all_rmsd = []
    lines_rmsd = []

    # --------------------------------------------------
    # Panel RMSD vs Tiempo
    # --------------------------------------------------
    for i, data in enumerate(all_data):
        time = data[:, 0]
        rmsd = data[:, 1]
        all_rmsd.append(rmsd)

        label = get_label_from_filename(input_files[i])
        color = COLOR_PALETTE[i % len(COLOR_PALETTE)]

        line, = ax_rmsd.plot(
            time,
            rmsd,
            linewidth=1.5,
            color=color,
            label=label,
            zorder=3
        )
        lines_rmsd.append(line)

    ax_rmsd.set_xlabel("Time (ns)", fontsize=14)
    ax_rmsd.set_ylabel("RMSD (nm)", fontsize=14)
    ax_rmsd.set_xlim(0, max_time)
    ax_rmsd.set_ylim(0, max_rmsd * 1.05)

    ax_rmsd.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)

    # Marco completo
    for spine in ax_rmsd.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1)

    ax_rmsd.tick_params(direction="out", length=6, width=1.2)

    # --------------------------------------------------
    # Panel PDF
    # --------------------------------------------------
    combined_rmsd = np.concatenate(all_rmsd)
    y_min, y_max = combined_rmsd.min(), combined_rmsd.max()
    x_vals = np.linspace(y_min, y_max, 400)

    for i, rmsd in enumerate(all_rmsd):
        kde = gaussian_kde(rmsd)
        pdf = kde(x_vals)
        color = COLOR_PALETTE[i % len(COLOR_PALETTE)]

        ax_pdf.plot(pdf, x_vals, color=color, linewidth=1.5)
        ax_pdf.fill_betweenx(x_vals, pdf, alpha=0.3, color=color)

    ax_pdf.set_xlabel("Density", fontsize=14)
    ax_pdf.set_xlim(left=0)

    ax_pdf.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)

    # Marco completo
    for spine in ax_pdf.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1)

    ax_pdf.tick_params(direction="out", length=6, width=1.2)
    ax_pdf.yaxis.set_visible(False)

    # --------------------------------------------------
    # Título superior
    # --------------------------------------------------
    fig.suptitle("RMSD Comparison", fontsize=16, y=0.96)

    # --------------------------------------------------
    # Leyenda global
    # --------------------------------------------------
    if len(input_files) > 1:
        legend = fig.legend(
            handles=lines_rmsd,
            labels=[line.get_label() for line in lines_rmsd],
            loc="lower center",
            bbox_to_anchor=(0.5, 0.02),
            ncol=min(len(lines_rmsd), 8),
            fontsize=11,
            frameon=True,
            fancybox=True,
            framealpha=1,
            edgecolor="black"
        )
        legend.get_frame().set_linewidth(0.8)

    # --------------------------------------------------
    # Ajustes de márgenes
    # --------------------------------------------------
    plt.subplots_adjust(
        left=0.08,
        right=0.98,
        top=0.90,
        bottom=0.20,
        wspace=0.05
    )

    # --------------------------------------------------
    # Guardar PDF vectorial
    # --------------------------------------------------
    plt.savefig(output_file, format="pdf", bbox_inches="tight")
    plt.close()