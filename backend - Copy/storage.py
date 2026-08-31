import os
import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "data/medcare.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


# ---------------- CREATE HEALTH TABLE ----------------

def create_health_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS health (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        senior TEXT NOT NULL,

        date TEXT,

        time TEXT,

        blood_pressure REAL,

        sugar_level REAL,

        heart_rate REAL,

        risk_level TEXT
    )
    """)

    conn.commit()
    conn.close()


create_health_table()


# ---------------- SAVE HEALTH RECORD ----------------

def save_health_record(senior, bp, sugar, hr, risk):

    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now()

    cursor.execute("""
        INSERT INTO health
        (
            senior,
            date,
            time,
            blood_pressure,
            sugar_level,
            heart_rate,
            risk_level
        )
        VALUES
        (?, ?, ?, ?, ?, ?, ?)
    """,
    (
        senior.lower(),
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M:%S"),
        bp,
        sugar,
        hr,
        risk
    ))

    conn.commit()
    conn.close()


# ---------------- GET LATEST HEALTH ----------------

def get_latest_health(senior):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            blood_pressure,
            sugar_level,
            heart_rate

        FROM health

        WHERE senior=?

        ORDER BY id DESC

        LIMIT 1
    """,
    (senior.lower(),))

    row = cursor.fetchone()

    conn.close()

    if row:
        return row

    return None, None, None


# ---------------- LAST 7 RECORDS ----------------

def get_last_7_records(senior):

    conn = get_connection()

    query = """
        SELECT
            date AS Date,
            time AS Time,
            blood_pressure AS 'Blood Pressure',
            sugar_level AS 'Sugar Level',
            heart_rate AS 'Heart Rate',
            risk_level AS 'Risk Level'

        FROM health

        WHERE senior=?

        ORDER BY id DESC

        LIMIT 7
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=(senior.lower(),)
    )

    conn.close()

    return df


# ---------------- FULL HISTORY ----------------

def get_all_records(senior):

    conn = get_connection()

    query = """
        SELECT
            date AS Date,
            time AS Time,
            blood_pressure AS 'Blood Pressure',
            sugar_level AS 'Sugar Level',
            heart_rate AS 'Heart Rate',
            risk_level AS 'Risk Level'

        FROM health

        WHERE senior=?

        ORDER BY id DESC
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=(senior.lower(),)
    )

    conn.close()

    return df
# ---------------- GET LATEST RISK ----------------

def get_latest_risk(senior):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT risk_level

        FROM health

        WHERE senior=?

        ORDER BY id DESC

        LIMIT 1
    """,
    (senior.lower(),))

    row = cursor.fetchone()

    conn.close()

    if row:
        return row[0]

    return None