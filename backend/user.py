import sqlite3
import hashlib
import random
import string

DB_PATH = "data/medcare.db"


# ---------------- DATABASE CONNECTION ----------------

def get_connection():
    return sqlite3.connect(DB_PATH)


# ---------------- PASSWORD HASH ----------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ---------------- CREATE USERS TABLE ----------------

def create_user_table():

    conn = get_connection()
    cursor = conn.cursor()

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

    conn.commit()
    conn.close()


# Create table automatically
create_user_table()

# ================= CREATE CONNECTIONS TABLE =================

def create_connections_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS connections (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        senior_username TEXT NOT NULL,

        caregiver_username TEXT NOT NULL,

        UNIQUE(senior_username, caregiver_username)
    )
    """)

    conn.commit()
    conn.close()


create_connections_table()


# ---------------- CONNECTION CODE ----------------

def generate_connection_code():

    while True:

        code = "MC-SNR-" + "".join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=8
            )
        )

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE connection_code=?",
            (code,)
        )

        exists = cursor.fetchone()

        conn.close()

        if not exists:
            return code


# ---------------- CREATE USER ----------------

def create_user(
    full_name,
    username,
    password,
    role,
    email,
    mobile,
    address=""
):

    conn = get_connection()
    cursor = conn.cursor()

    username = username.strip().lower()
    email = email.strip().lower()

    cursor.execute(
        "SELECT id FROM users WHERE username=?",
        (username,)
    )

    if cursor.fetchone():

        conn.close()
        return False

    password_hash = hash_password(password)

    connection_code = ""

    if role == "Senior":
        connection_code = generate_connection_code()

    cursor.execute("""
    INSERT INTO users
    (
        full_name,
        username,
        password,
        role,
        email,
        mobile,
        address,
        connection_code
    )

    VALUES
    (?, ?, ?, ?, ?, ?, ?, ?)
""",
(
    full_name,
    username,
    password_hash,
    role,
    email,
    mobile,
    address,
    connection_code
))

    conn.commit()
    conn.close()

    return True


# ---------------- LOGIN ----------------

def authenticate_user(username, password):

    conn = get_connection()
    cursor = conn.cursor()

    username = username.strip().lower()
    password_hash = hash_password(password)

    cursor.execute("""
        SELECT role
        FROM users
        WHERE username=?
        AND password=?
    """,
    (
        username,
        password_hash
    ))

    row = cursor.fetchone()

    conn.close()

    if row:
        return row[0]

    return None


# ---------------- GET USER ----------------

def get_user(username):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (username.lower(),)
    )

    row = cursor.fetchone()

    conn.close()

    return row


# ---------------- GET CONNECTION CODE ----------------

def get_connection_code(username):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT connection_code
        FROM users
        WHERE username=?
    """,
    (
        username.lower(),
    ))

    row = cursor.fetchone()

    conn.close()

    if row:
        return row[0]

    return None

# ---------------- VERIFY CONNECTION CODE ----------------

def verify_connection_code(connection_code):

    conn = get_connection()
    cursor = conn.cursor()

    connection_code = connection_code.strip().upper()

    cursor.execute("""
        SELECT username
        FROM users
        WHERE connection_code=?
        AND role='Senior'
    """, (connection_code,))

    row = cursor.fetchone()

    conn.close()

    return row is not None


# ---------------- CONNECT CAREGIVER TO SENIOR ----------------

def connect_caregiver_to_senior(connection_code, caregiver):

    conn = get_connection()
    cursor = conn.cursor()

    caregiver = caregiver.strip().lower()
    connection_code = connection_code.strip().upper()

    cursor.execute("""
        SELECT username
        FROM users
        WHERE connection_code=?
        AND role='Senior'
    """, (connection_code,))

    row = cursor.fetchone()

    if row is None:
        conn.close()
        return False

    senior_username = row[0]

    cursor.execute("""
        INSERT OR IGNORE INTO connections
        (
            senior_username,
            caregiver_username
        )
        VALUES (?, ?)
    """,
    (
        senior_username,
        caregiver
    ))

    conn.commit()
    conn.close()

    return True


# ---------------- CONNECT CAREGIVER ----------------

def connect_caregiver(caregiver_username, connection_code):

    return connect_caregiver_to_senior(
        connection_code,
        caregiver_username
    )

# ---------------- GET MY SENIORS ----------------

def get_my_seniors(caregiver):

    conn = get_connection()
    cursor = conn.cursor()

    caregiver = caregiver.strip().lower()

    cursor.execute("""
        SELECT senior_username
        FROM connections
        WHERE caregiver_username=?
        ORDER BY senior_username
    """, (caregiver,))

    rows = cursor.fetchall()

    conn.close()

    return [row[0] for row in rows]

# ---------------- GET CONNECTED CAREGIVERS ----------------

def get_connected_caregivers(senior):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            users.full_name,
            users.username,
            users.email,
            users.mobile

        FROM connections

        JOIN users
        ON connections.caregiver_username = users.username

        WHERE connections.senior_username=?

        ORDER BY users.full_name
    """,
    (
        senior.lower(),
    ))

    rows = cursor.fetchall()

    conn.close()

    return rows
# ---------------- GET USER EMAIL ----------------

def get_user_email(username):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT email
        FROM users
        WHERE username=?
    """,
    (username.lower(),))

    row = cursor.fetchone()

    conn.close()

    if row:
        return row[0]

    return None


# ---------------- GET USER MOBILE ----------------

def get_user_mobile(username):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT mobile
        FROM users
        WHERE username=?
    """,
    (username.lower(),))

    row = cursor.fetchone()

    conn.close()

    if row:
        return row[0]

    return None