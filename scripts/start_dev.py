#!/usr/bin/env python3
"""
SchoolRail Development Server Starter
Starts all services for development.
"""

import subprocess
import sys
import os

def start_backend():
    print("Starting backend server on port 3001...")
    subprocess.Popen(
        [sys.executable, "main.py"],
        cwd="backend"
    )

def start_admin():
    print("Starting admin panel on port 3000...")
    subprocess.Popen(
        ["npm", "run", "dev"],
        cwd="admin"
    )

def main():
    print("SchoolRail Development Server")
    print("=" * 50)
    print("Backend: http://localhost:3001")
    print("Admin: http://localhost:3000")
    print("API Docs: http://localhost:3001/docs")
    print("=" * 50)

    start_backend()
    start_admin()

    print("\nServers started. Press Ctrl+C to stop.")

if __name__ == "__main__":
    main()