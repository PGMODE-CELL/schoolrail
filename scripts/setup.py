#!/usr/bin/env python3
"""
SchoolRail Setup Script
Initializes the project for development.
"""

import os
import sys
import subprocess

def create_env_file():
    env_example = "backend/.env.example"
    env_file = "backend/.env"

    if not os.path.exists(env_file):
        if os.path.exists(env_example):
            with open(env_example, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print(f"Created {env_file} from template")
        else:
            print(f"Warning: {env_example} not found")

def install_backend():
    print("\nInstalling backend dependencies...")
    os.chdir("backend")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    os.chdir("..")

def install_frontend():
    print("\nInstalling admin dependencies...")
    os.chdir("admin")
    subprocess.run(["npm", "install"])
    os.chdir("..")

def init_database():
    print("\nInitializing database with seed data...")
    os.chdir("backend")
    subprocess.run([sys.executable, "seed_data.py"])
    os.chdir("..")

def main():
    print("SchoolRail Setup")
    print("=" * 50)

    create_env_file()

    install_backend()
    install_frontend()
    init_database()

    print("\nSetup complete!")
    print("\nTo run the backend:")
    print("  cd backend && python main.py")
    print("\nTo run the admin:")
    print("  cd admin && npm run dev")

if __name__ == "__main__":
    main()