#!/usr/bin/env python3
"""Test runner script."""

import subprocess
import sys
from pathlib import Path

def main():
    """Run the test suite."""
    project_root = Path(__file__).parent.parent
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        str(project_root / "tests"),
        "-v",
        "--tb=short",
        "--cov=pha",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov"
    ]
    
    try:
        result = subprocess.run(cmd, cwd=project_root, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with exit code: {e.returncode}")
        return e.returncode

if __name__ == "__main__":
    sys.exit(main())