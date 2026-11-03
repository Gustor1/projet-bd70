"""Compatibility entry point for the current report generator."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('build-report-final.py')),run_name='__main__')
