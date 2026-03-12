import numpy as np
from pathlib import Path

def read_xvg(file_path: Path) -> np.ndarray:
    """Reads GROMACS XVG files and returns a numpy array."""
    data = []
    with open(file_path, "r") as f:
        for line in f:
            if line.startswith(("#", "@")):
                continue
            data.append([float(x) for x in line.split()])
    return np.array(data)
