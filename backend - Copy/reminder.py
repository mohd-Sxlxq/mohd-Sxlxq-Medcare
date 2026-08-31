import sqlite3
import pandas as pd

DB_PATH = "data/medcare.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


# ---------------- CREATE REMINDER TABLE ----------------

def create_reminder_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        senior TEXT NOT NULL,

        medicine TEXT NOT NULL,

        start_time TEXT,

        end_time TEXT,

        taken TEXT DEFAULT 'No',

        notified TEXT DEFAULT 'No'
    )
    """)

    conn.commit()
    conn.close()


create_reminder_table()


# ---------------- SAVE REMINDER ----------------

def save_reminder(medicine, start_time, end_time, senior):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reminders
        (
            senior,
            medicine,
            start_time,
            end_time,
            taken,
            notified
        )
        VALUES
        (?, ?, ?, ?, 'No', 'No')
    """,
    (
        senior.lower(),
        medicine,
        start_time,
        end_time
    ))

    conn.commit()
    conn.close()


# ---------------- GET REMINDERS ----------------

def get_reminders_for_senior(senior):

    conn = get_connection()

    query = """
        SELECT
            id,
            medicine AS Medicine,
            start_time AS Start,
            end_time AS End,
            taken AS Taken,
            notified AS Notified

        FROM reminders

        WHERE senior=?

        ORDER BY start_time
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=(senior.lower(),)
    )

    conn.close()

    return df


# ---------------- MARK AS TAKEN ----------------

def mark_taken(reminder_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE reminders
        SET taken='Yes'
        WHERE id=?
    """, (reminder_id,))

    conn.commit()
    conn.close()


# ---------------- MARK AS NOTIFIED ----------------

def mark_notified(reminder_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE reminders
        SET notified='Yes'
        WHERE id=?
    """, (reminder_id,))

    conn.commit()
    conn.close()