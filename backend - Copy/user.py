import hashlib
import random
import string

from backend.supabase_client import supabase


# =========================================================
# PASSWORD HASH
# =========================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# =========================================================
# CONNECTION CODE
# =========================================================

def generate_connection_code():

    while True:

        code = "MC-SNR-" + "".join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=8
            )
        )

        response = (
            supabase
            .table("users")
            .select("id")
            .eq("connection_code", code)
            .execute()
        )

        if not response.data:
            return code


# =========================================================
# CREATE USER / REGISTER
# =========================================================

def create_user(
    full_name,
    username,
    password,
    role,
    email,
    mobile,
    address=""
):

    username = username.strip().lower()
    email = email.strip().lower()
    role = role.strip().title()

    # Check whether username already exists
    response = (
        supabase
        .table("users")
        .select("id")
        .eq("username", username)
        .execute()
    )

    if response.data:
        return False

    password_hash = hash_password(password)

    connection_code = None

    # Only Senior gets a connection code
    if role == "Senior":
        connection_code = generate_connection_code()

    try:

        supabase.table("users").insert({
            "full_name": full_name.strip(),
            "username": username,
            "password": password_hash,
            "role": role,
            "email": email,
            "mobile": mobile.strip(),
            "address": address.strip(),
            "connection_code": connection_code
        }).execute()

        return True

    except Exception as e:

        print("❌ Create user error:", e)
        return False


# =========================================================
# LOGIN
# =========================================================

def authenticate_user(username, password):

    username = username.strip().lower()
    password_hash = hash_password(password)

    try:

        response = (
            supabase
            .table("users")
            .select("role")
            .eq("username", username)
            .eq("password", password_hash)
            .execute()
        )

        if response.data:
            return response.data[0]["role"]

        return None

    except Exception as e:

        print("❌ Authentication error:", e)
        return None


# =========================================================
# GET USER
# =========================================================

def get_user(username):

    username = username.strip().lower()

    try:

        response = (
            supabase
            .table("users")
            .select("*")
            .eq("username", username)
            .execute()
        )

        if response.data:
            return response.data[0]

        return None

    except Exception as e:

        print("❌ Get user error:", e)
        return None


# =========================================================
# GET CONNECTION CODE
# =========================================================

def get_connection_code(username):

    username = username.strip().lower()

    try:

        response = (
            supabase
            .table("users")
            .select("connection_code")
            .eq("username", username)
            .execute()
        )

        if response.data:
            return response.data[0]["connection_code"]

        return None

    except Exception as e:

        print("❌ Connection code error:", e)
        return None


# =========================================================
# VERIFY CONNECTION CODE
# =========================================================

def verify_connection_code(connection_code):

    connection_code = connection_code.strip().upper()

    try:

        response = (
            supabase
            .table("users")
            .select("username")
            .eq("connection_code", connection_code)
            .eq("role", "Senior")
            .execute()
        )

        return bool(response.data)

    except Exception as e:

        print("❌ Verify connection code error:", e)
        return False


# =========================================================
# CONNECT CAREGIVER TO SENIOR
# =========================================================

def connect_caregiver_to_senior(
    connection_code,
    caregiver
):

    caregiver = caregiver.strip().lower()
    connection_code = connection_code.strip().upper()

    try:

        # Find Senior using connection code
        response = (
            supabase
            .table("users")
            .select("username")
            .eq("connection_code", connection_code)
            .eq("role", "Senior")
            .execute()
        )

        if not response.data:
            return False

        senior_username = response.data[0]["username"]

        # Make sure caregiver exists
        caregiver_response = (
            supabase
            .table("users")
            .select("username")
            .eq("username", caregiver)
            .eq("role", "Caregiver")
            .execute()
        )

        if not caregiver_response.data:
            return False

        # Create connection
        supabase.table("connections").insert({
            "senior_username": senior_username,
            "caregiver_username": caregiver
        }).execute()

        return True

    except Exception as e:

        # Duplicate connection is not a fatal application error
        if "duplicate" in str(e).lower():
            return True

        print("❌ Caregiver connection error:", e)
        return False


# =========================================================
# CONNECT CAREGIVER
# =========================================================

def connect_caregiver(
    caregiver_username,
    connection_code
):

    return connect_caregiver_to_senior(
        connection_code,
        caregiver_username
    )


# =========================================================
# GET MY SENIORS
# =========================================================

def get_my_seniors(caregiver):

    caregiver = caregiver.strip().lower()

    try:

        response = (
            supabase
            .table("connections")
            .select("senior_username")
            .eq("caregiver_username", caregiver)
            .order("senior_username")
            .execute()
        )

        return [
            row["senior_username"]
            for row in response.data
        ]

    except Exception as e:

        print("❌ Get seniors error:", e)
        return []


# =========================================================
# GET CONNECTED CAREGIVERS
# =========================================================

def get_connected_caregivers(senior):

    senior = senior.strip().lower()

    try:

        response = (
            supabase
            .table("connections")
            .select(
                "caregiver_username"
            )
            .eq("senior_username", senior)
            .order("caregiver_username")
            .execute()
        )

        results = []

        for connection in response.data:

            caregiver_username = connection["caregiver_username"]

            caregiver_response = (
                supabase
                .table("users")
                .select(
                    "full_name,username,email,mobile"
                )
                .eq("username", caregiver_username)
                .execute()
            )

            if caregiver_response.data:
                caregiver = caregiver_response.data[0]

                results.append((
                    caregiver["full_name"],
                    caregiver["username"],
                    caregiver["email"],
                    caregiver["mobile"]
                ))

        return results

    except Exception as e:

        print("❌ Get caregivers error:", e)
        return []


# =========================================================
# GET USER EMAIL
# =========================================================

def get_user_email(username):

    username = username.strip().lower()

    try:

        response = (
            supabase
            .table("users")
            .select("email")
            .eq("username", username)
            .execute()
        )

        if response.data:
            return response.data[0]["email"]

        return None

    except Exception as e:

        print("❌ Get email error:", e)
        return None


# =========================================================
# GET USER MOBILE
# =========================================================

def get_user_mobile(username):

    username = username.strip().lower()

    try:

        response = (
            supabase
            .table("users")
            .select("mobile")
            .eq("username", username)
            .execute()
        )

        if response.data:
            return response.data[0]["mobile"]

        return None

    except Exception as e:

        print("❌ Get mobile error:", e)
        return None