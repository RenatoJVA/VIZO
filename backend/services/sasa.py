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

COLOR_PALETTE = [
    "#000000", "#8d25a7", "#d141c7", "#e170c0", "#c52a91",
    "#a70e62", "#85113d", "#630f5b", "#541191", "#4915be",
    "#101167", "#2d3280", "#2357d5", "#5b98f4"
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
    return os.path.basename(filepath).replace("-sasa.xvg", "")

# --------------------------------------------------
# Plot SASA
# --------------------------------------------------
def plot_sasa(input_files, output_file):

    if isinstance(input_files, str):
        input_files = [input_files]

    all_data = []
    max_time = 0
    max_sasa = 0

    for file in input_files:
        data = read_xvg(file)
        all_data.append(data)
        max_time = max(max_time, data[:, 0].max())
        max_sasa = max(max_sasa, data[:, 1].max())

    fig = plt.figure(figsize=(14, 6))
    gs = GridSpec(1, 2, width_ratios=[7, 3])

    ax_main = fig.add_subplot(gs[0])
    ax_pdf = fig.add_subplot(gs[1], sharey=ax_main)

    all_values = []
    lines = []

    # -----------------------------
    # Panel principal
    # -----------------------------
    for i, data in enumerate(all_data):
        time = data[:, 0]
        sasa = data[:, 1]
        all_values.append(sasa)

        label = get_label_from_filename(input_files[i])
        color = COLOR_PALETTE[i % len(COLOR_PALETTE)]

        line, = ax_main.plot(time, sasa,
                             linewidth=1.5,
                             color=color,
                             label=label)
        lines.append(line)

    ax_main.set_xlabel("Time (ns)", fontsize=14)
    ax_main.set_ylabel("SASA (nm²)", fontsize=14)
    ax_main.set_xlim(0, max_time)
    ax_main.set_ylim(0, max_sasa * 1.05)

    ax_main.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)

    for spine in ax_main.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1)

    ax_main.tick_params(direction="out", length=6, width=1.2)

    # -----------------------------
    # Panel KDE
    # -----------------------------
    combined = np.concatenate(all_values)
    y_vals = np.linspace(combined.min(), combined.max(), 400)

    for i, values in enumerate(all_values):
        kde = gaussian_kde(values)
        pdf = kde(y_vals)
        color = COLOR_PALETTE[i % len(COLOR_PALETTE)]

        ax_pdf.plot(pdf, y_vals, color=color)
        ax_pdf.fill_betweenx(y_vals, pdf, alpha=0.3, color=color)

    ax_pdf.set_xlabel("Density", fontsize=14)
    ax_pdf.set_xlim(left=0)
    ax_pdf.yaxis.set_visible(False)

    for spine in ax_pdf.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1)

    ax_pdf.tick_params(direction="out", length=6, width=1.2)

    # -----------------------------
    # Título
    # -----------------------------
    fig.suptitle("Solvent Accessible Surface Area (SASA)", fontsize=16, y=0.96)

    # -----------------------------
    # Leyenda
    # -----------------------------
    if len(input_files) > 1:
        legend = fig.legend(
            handles=lines,
            labels=[l.get_label() for l in lines],
            loc="lower center",
            bbox_to_anchor=(0.5, 0.02),
            ncol=min(len(lines), 8),
            frameon=True,
            edgecolor="black"
        )
        legend.get_frame().set_linewidth(0.8)

    plt.subplots_adjust(left=0.08, right=0.98,
                        top=0.90, bottom=0.20, wspace=0.05)

    plt.savefig(output_file, format="pdf", bbox_inches="tight")
    plt.close()