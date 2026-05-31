#!/usr/bin/env python3
"""
SchoolRail Test Runner
Runs all tests.
"""

import subprocess
import sys
import os

def run_tests():
    print("Running backend tests...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "backend/tests/", "-v"],
        cwd=os.path.dirname(os.path.dirname(__file__))
    )
    return result.returncode

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)