from .theme import scientific_style, COLOR_PALETTE
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.stats import gaussian_kde
from pathlib import Path
from typing import List
from ..xvg_parser import read_xvg

class MDPlotter:
    def __init__(
        self, 
        title: str, 
        xlabel: str, 
        ylabel: str, 
        suffix: str,
        show_kde: bool = True
    ):
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.suffix = suffix
        self.show_kde = show_kde

    def get_label(self, path: Path) -> str:
        return path.name.replace(self.suffix, "").replace("-", " ").strip()

    @scientific_style
    def plot(self, input_files: List[Path], output_file: Path) -> None:
        all_data = [read_xvg(f) for f in input_files]
        
        max_x = max(d[:, 0].max() for d in all_data)
        max_y = max(d[:, 1].max() for d in all_data)
        
        fig = plt.figure(figsize=(14, 6))
        
        if self.show_kde:
            gs = GridSpec(1, 2, width_ratios=[7, 3])
            ax_main = fig.add_subplot(gs[0])
            ax_kde = fig.add_subplot(gs[1], sharey=ax_main)
        else:
            ax_main = fig.add_subplot(111)
            ax_kde = None

        lines = []
        all_y_values = []

        for i, data in enumerate(all_data):
            x, y = data[:, 0], data[:, 1]
            all_y_values.append(y)
            color = COLOR_PALETTE[i % len(COLOR_PALETTE)]
            label = self.get_label(input_files[i])
            
            line, = ax_main.plot(x, y, linewidth=1.5, color=color, label=label, zorder=3)
            lines.append(line)

        # Main Panel Config
        ax_main.set_xlabel(self.xlabel, fontsize=14)
        ax_main.set_ylabel(self.ylabel, fontsize=14)
        ax_main.set_xlim(0, max_x)
        ax_main.set_ylim(0, max_y * 1.05)
        ax_main.grid(True)

        if ax_kde:
            combined_y = np.concatenate(all_y_values)
            y_min, y_max = combined_y.min(), combined_y.max()
            
            # Si el rango es 0 (datos constantes), no podemos hacer KDE
            if y_min == y_max:
                ax_kde.text(0.5, 0.5, "Sin varianza\n(Datos constantes)", 
                            ha='center', va='center', transform=ax_kde.transAxes)
            else:
                y_range = np.linspace(y_min, y_max, 400)
                for i, y in enumerate(all_y_values):
                    # Solo calculamos KDE si hay varianza en este set específico
                    if np.var(y) > 0:
                        color = COLOR_PALETTE[i % len(COLOR_PALETTE)]
                        kde = gaussian_kde(y)
                        density = kde(y_range)
                        ax_kde.plot(density, y_range, color=color, linewidth=1.5)
                        ax_kde.fill_betweenx(y_range, density, alpha=0.3, color=color)
            
            ax_kde.set_xlabel("Density", fontsize=14)
            ax_kde.set_xlim(left=0)
            ax_kde.yaxis.set_visible(False)
            ax_kde.grid(True)

        fig.suptitle(self.title, fontsize=16, y=0.96)

        if len(input_files) > 1:
            legend = fig.legend(
                handles=lines,
                loc="lower center",
                bbox_to_anchor=(0.5, 0.02),
                ncol=min(len(lines), 8),
                fontsize=11,
                frameon=True,
                edgecolor="black"
            )
            legend.get_frame().set_linewidth(0.8)

        plt.subplots_adjust(left=0.08, right=0.98, top=0.90, bottom=0.20, wspace=0.05)
        plt.savefig(output_file, format="pdf", bbox_inches="tight")
