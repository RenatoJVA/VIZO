from typing import Protocol, List
from pathlib import Path

class Plotter(Protocol):
    """Protocol for all MD analysis plotters."""
    def plot(self, input_files: List[Path], output_file: Path) -> None:
        ...
