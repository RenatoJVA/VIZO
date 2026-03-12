import matplotlib
matplotlib.use('Agg') # Requerido para evitar warnings de hilos en servidores
import matplotlib.pyplot as plt
import functools

COLOR_PALETTE = [
    "#000000", "#8d25a7", "#d141c7", "#e170c0", "#c52a91",
    "#a70e62", "#85113d", "#630f5b", "#541191", "#4915be",
    "#101167", "#2d3280", "#2357d5", "#5b98f4", "#5892be",
    "#6ecad5", "#207b7d", "#2b8753", "#5ba349", "#8ed73d",
    "#bbde01", "#f0c53a", "#d48d08", "#8a4032", "#fc843a",
    "#f25829", "#e00233", "#455894"
]

def scientific_style(func):
    """Decorator to apply scientific plotting styles to a function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        plt.rcParams.update({
            'font.family': 'Times New Roman',
            'pdf.fonttype': 42,
            'ps.fonttype': 42,
            'axes.linewidth': 1,
            'grid.alpha': 0.3,
            'grid.linestyle': '--',
            'grid.linewidth': 0.5,
            'xtick.direction': 'out',
            'ytick.direction': 'out',
            'xtick.major.size': 6,
            'ytick.major.size': 6,
            'xtick.major.width': 1.2,
            'ytick.major.width': 1.2,
        })
        try:
            return func(*args, **kwargs)
        finally:
            plt.close('all')
    return wrapper
