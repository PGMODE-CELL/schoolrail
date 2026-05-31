#!/usr/bin/env python3
"""
SchoolRail Backup Script
Creates database backups.
"""

import os
import shutil
import datetime
from pathlib import Path

def backup_database():
    db_path = "backend/schoolrail.db"
    backup_dir = "backups"

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"schoolrail_backup_{timestamp}.db"

    shutil.copy2(db_path, os.path.join(backup_dir, backup_file))

    print(f"Backup created: {backup_dir}/{backup_file}")

    keep = 7
    backups = sorted(Path(backup_dir).glob("*.db"))
    for old in backups[:-keep]:
        os.remove(old)
        print(f"Removed old backup: {old}")

if __name__ == "__main__":
    backup_database()