"""Compatibility entry point for the current evidence-based documentation."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("finalize-completion.py")),run_name="__main__")
