import tempfile
import shutil
from pathlib import Path
from typing import Generator

def get_temp_dir() -> Generator[Path, None, None]:
    """Provides a temporary directory that is automatically cleaned up."""
    tmp_path = Path(tempfile.mkdtemp())
    try:
        yield tmp_path
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)
