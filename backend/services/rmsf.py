import numpy as np
import matplotlib.pyplot as plt
import os

# --------------------------------------------------
# Configuración global
# --------------------------------------------------
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['pdf.fonttype'] = 42  # Texto editable en Illustrator
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
# Leer archivo XVG
# --------------------------------------------------
def read_xvg(file):
    data = []
    with open(file) as f:
        for line in f:
            if line.startswith(("#", "@")):
                continue
            data.append([float(x) for x in line.split()])
    return np.array(data)

# --------------------------------------------------
# Obtener etiqueta limpia
# --------------------------------------------------
def get_label_from_filename(filepath):
    basename = os.path.basename(filepath)
    return basename.replace("-rmsf.xvg", "")

# --------------------------------------------------
# Plot RMSF
# --------------------------------------------------
def plot_rmsf(input_files, output_file):

    if isinstance(input_files, str):
        input_files = [input_files]

    all_data = []
    max_residue = 0
    max_rmsf = 0

    for file in input_files:
        data = read_xvg(file)
        all_data.append(data)
        max_residue = max(max_residue, data[:, 0].max())
        max_rmsf = max(max_rmsf, data[:, 1].max())

    # Crear figura
    fig, ax = plt.subplots(figsize=(14, 6))

    # Plotear curvas
    for i, data in enumerate(all_data):
        residue = data[:, 0]
        rmsf = data[:, 1]
        label = get_label_from_filename(input_files[i])
        color = COLOR_PALETTE[i % len(COLOR_PALETTE)]

        ax.plot(
            residue,
            rmsf,
            linewidth=1.8,
            color=color,
            label=label if len(input_files) > 1 else None,
            zorder=3
        )

    # Etiquetas
    ax.set_xlabel("Residue Number", fontsize=14)
    ax.set_ylabel("RMSF (nm)", fontsize=14)

    # Límites
    ax.set_xlim(0, max_residue)
    ax.set_ylim(0, max_rmsf * 1.05)

    # Cuadro completo (todas las spines)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1)

    # Grid sutil
    ax.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)

    # Ticks estilo clásico
    ax.tick_params(direction="out", length=6, width=1.2)

    # Título superior (figura completa)
    fig.suptitle("RMSF Comparison", fontsize=16, y=0.96)

    # Leyenda global (si hay múltiples archivos)
    if len(input_files) > 1:
        legend = fig.legend(
            handles=ax.get_lines(),
            labels=[line.get_label() for line in ax.get_lines()],
            loc="lower center",
            bbox_to_anchor=(0.5, 0.02),
            ncol=min(len(input_files), 8),
            fontsize=11,
            frameon=True,
            fancybox=True,
            framealpha=1,
            edgecolor="black"
        )
        legend.get_frame().set_linewidth(0.8)

    # Ajuste manual de márgenes
    plt.subplots_adjust(
        left=0.08,
        right=0.98,
        top=0.90,
        bottom=0.18 if len(input_files) > 1 else 0.10
    )

    # Guardar PDF vectorial
    plt.savefig(output_file, format="pdf", bbox_inches="tight")
    plt.close()