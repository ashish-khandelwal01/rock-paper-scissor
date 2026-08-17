import sys
from pathlib import Path
import runpy

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

runpy.run_path(
    project_root / "main.py",
    run_name="__main__",
)