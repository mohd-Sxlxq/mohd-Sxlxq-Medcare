import sqlite3
import os
from backend.supabase_client import supabase

# Create data folder if it doesn't exist
os.makedirs("data", exist_ok=True)

DB_PATH = "data/medcare.db"


def create_database():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # =====================================================
    # USERS TABLE
    # =====================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        full_name TEXT NOT NULL,

        username TEXT UNIQUE NOT NULL,

        password TEXT NOT NULL,

        role TEXT NOT NULL,

        email TEXT NOT NULL,

        mobile TEXT NOT NULL,

        address TEXT,

        connection_code TEXT UNIQUE
    )
    """)

    # =====================================================
    # CONNECTIONS TABLE
    # One Senior -> Many Caregivers
    # =====================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS connections (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        senior_username TEXT NOT NULL,

        caregiver_username TEXT NOT NULL,

        UNIQUE(
            senior_username,
            caregiver_username
        ),

        FOREIGN KEY(senior_username)
            REFERENCES users(username),

        FOREIGN KEY(caregiver_username)
            REFERENCES users(username)
    )
    """)

    conn.commit()
    conn.close()

    print("✅ MedCare database created successfully.")


if __name__ == "__main__":
    create_database()