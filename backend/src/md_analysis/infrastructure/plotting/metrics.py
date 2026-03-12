from .engine import MDPlotter

# Define specific plotters as instances with fixed configuration
RMSD_PLOTTER = MDPlotter(
    title="RMSD Comparison",
    xlabel="Time (ns)",
    ylabel="RMSD (nm)",
    suffix="-rmsd.xvg"
)

SASA_PLOTTER = MDPlotter(
    title="Solvent Accessible Surface Area (SASA)",
    xlabel="Time (ns)",
    ylabel="SASA (nm²)",
    suffix="-sasa.xvg"
)

RG_PLOTTER = MDPlotter(
    title="Radius of Gyration (Rg)",
    xlabel="Time (ns)",
    ylabel="Radius of Gyration (nm)",
    suffix="-rg.xvg"
)

HBNUM_PLOTTER = MDPlotter(
    title="Hydrogen Bonds (hbnum)",
    xlabel="Time (ns)",
    ylabel="Number of Hydrogen Bonds",
    suffix="-hbnum.xvg"
)

RMSF_PLOTTER = MDPlotter(
    title="RMSF Comparison",
    xlabel="Residue Number",
    ylabel="RMSF (nm)",
    suffix="-rmsf.xvg",
    show_kde=False # RMSF usually doesn't show KDE as X is residue index, not time
)

METRIC_MAP = {
    "rmsd": RMSD_PLOTTER,
    "sasa": SASA_PLOTTER,
    "rg": RG_PLOTTER,
    "hbnum": HBNUM_PLOTTER,
    "rmsf": RMSF_PLOTTER
}
