#!/usr/bin/env python3
"""
SchoolRail Data Seeder
Populates database with sample data.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from seed_data import seed

if __name__ == "__main__":
    print("Seeding database with sample data...")
    seed()
    print("Database seeded successfully!")