"""
=========================================================
MedCare Database Module
Backend : Supabase
=========================================================
"""

from backend.supabase_client import supabase


# =========================================================
# CONNECTION TEST
# =========================================================

def test_connection():
    """
    Test Supabase connection.
    """

    try:
        response = (
            supabase
            .table("users")
            .select("*")
            .limit(1)
            .execute()
        )

        print("✅ Supabase Connected Successfully")
        return True

    except Exception as e:
        print(f"❌ Supabase Connection Error:\n{e}")
        return False


# =========================================================
# USER FUNCTIONS
# =========================================================

def create_user(
    full_name,
    username,
    password,
    role,
    email,
    mobile,
    address,
    connection_code
):
    """
    Register new user.
    """

    try:

        response = (
            supabase
            .table("users")
            .insert({
                "full_name": full_name,
                "username": username,
                "password": password,
                "role": role,
                "email": email,
                "mobile": mobile,
                "address": address,
                "connection_code": connection_code
            })
            .execute()
        )

        return response.data

    except Exception as e:
        print(e)
        return None


def get_user(username):

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
        print(e)
        return None


def get_user_by_connection_code(code):

    try:

        response = (
            supabase
            .table("users")
            .select("*")
            .eq("connection_code", code)
            .execute()
        )

        if response.data:
            return response.data[0]

        return None

    except Exception as e:
        print(e)
        return None


# =========================================================
# CONNECTION FUNCTIONS
# =========================================================

def connect_caregiver(
    senior_username,
    caregiver_username
):

    try:

        response = (
            supabase
            .table("connections")
            .insert({
                "senior_username": senior_username,
                "caregiver_username": caregiver_username
            })
            .execute()
        )

        return response.data

    except Exception as e:
        print(e)
        return None


def get_connected_caregivers(
    senior_username
):

    try:

        response = (
            supabase
            .table("connections")
            .select("*")
            .eq("senior_username", senior_username)
            .execute()
        )

        return response.data

    except Exception as e:
        print(e)
        return []


def get_connected_seniors(
    caregiver_username
):

    try:

        response = (
            supabase
            .table("connections")
            .select("*")
            .eq("caregiver_username", caregiver_username)
            .execute()
        )

        return response.data

    except Exception as e:
        print(e)
        return []


# =========================================================
# DELETE FUNCTIONS
# =========================================================

def delete_connection(
    senior_username,
    caregiver_username
):

    try:

        response = (
            supabase
            .table("connections")
            .delete()
            .eq("senior_username", senior_username)
            .eq("caregiver_username", caregiver_username)
            .execute()
        )

        return response.data

    except Exception as e:
        print(e)
        return None


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    test_connection()