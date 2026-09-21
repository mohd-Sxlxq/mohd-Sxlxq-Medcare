import hashlib
import random
import string
from typing import Any

from backend.supabase_client import supabase


# =========================================================
# PASSWORD HASH
# =========================================================

def hash_password(password):

    return hashlib.sha256(password.encode()).hexdigest()


# =========================================================
# GENERATE SENIOR CONNECTION CODE
# =========================================================

def generate_connection_code():

    while True:

        code = "MC-SNR-" + "".join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=8
            )
        )

        try:

            response: Any = (
                supabase
                .table("users")
                .select("id")
                .eq("connection_code", code)
                .execute()
            )

            if not response.data:
                return code

        except Exception as e:

            print("❌ Connection code generation error:", e)
            return None


# =========================================================
# CREATE USER
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
    real_email = email.strip().lower()
    role = role.strip().title()

    try:
        # Check if username already exists in our table
        response: Any = (
            supabase
            .table("users")
            .select("username")
            .eq("username", username)
            .execute()
        )

        if response.data:
            return False, "Username already exists."

    except Exception as e:
        print("❌ Username check error:", e)
        return False, "Database connection error while checking username."

    connection_code = None

    if role == "Senior":
        connection_code = generate_connection_code()

        if connection_code is None:
            return False, "Failed to generate connection code."

    # Create a unique system email for Supabase Auth to bypass restrictions
    system_auth_email = f"{username}@medcare-system.local"

    try:
        # Step 1: Try to create the Auth account
        try:
            auth_response: Any = supabase.auth.sign_up({
                "email": system_auth_email,
                "password": password
            })
            
            if not auth_response.user:
                return False, "Supabase Auth registration failed."
                
            auth_id = str(auth_response.user.id)
            
        except Exception as auth_e:
            auth_error_msg = str(auth_e).lower()
            # GHOST ACCOUNT AUTO-HEALER
            if "already registered" in auth_error_msg or "already exists" in auth_error_msg:
                try:
                    # If it's a ghost account, log into it to recover the ID
                    recover_response: Any = supabase.auth.sign_in_with_password({
                        "email": system_auth_email,
                        "password": password
                    })
                    auth_id = str(recover_response.user.id)
                except Exception:
                    return False, "This username is permanently locked by a previous password mismatch. Please choose a new username."
            else:
                # If it's a different error (like password too short), raise it
                raise auth_e

        # Step 2: Create MedCare profile saving the REAL email for alerts
        supabase.table("users").insert({
            "full_name": full_name.strip(),
            "username": username,
            "password": hash_password(password),
            "role": role,
            "email": real_email,
            "mobile": mobile.strip(),
            "address": address.strip(),
            "connection_code": connection_code,
            "auth_id": auth_id
        }).execute()

        print("✅ User registered successfully.")
        return True, "Account created successfully."

    except Exception as e:
        error_msg = str(e)
        print("❌ Create user error:", error_msg)
        
        if "characters" in error_msg.lower() or "password" in error_msg.lower():
            return False, "Password must be at least 6 characters long."
            
        return False, f"Registration failed: {error_msg}"


# =========================================================
# LOGIN
# =========================================================

def authenticate_user(username, password):

    username = username.strip().lower()
    system_auth_email = f"{username}@medcare-system.local"

    try:
        # Get user details from our table
        response: Any = (
            supabase
            .table("users")
            .select("*")
            .eq("username", username)
            .execute()
        )

        if not response.data:
            print("❌ User not found.")
            return None

        user: Any = response.data[0]
        stored_real_email = user.get("email", "")

        # Try logging in with the system email first
        try:
            auth_response: Any = supabase.auth.sign_in_with_password({
                "email": system_auth_email,
                "password": password
            })
        except Exception:
            # Fallback for old accounts that registered before this fix
            auth_response: Any = supabase.auth.sign_in_with_password({
                "email": stored_real_email,
                "password": password
            })

        if not auth_response.user:
            print("❌ Supabase login failed.")
            return None

        # Verify Auth ID
        if user.get("auth_id"):
            if str(auth_response.user.id) != str(user.get("auth_id")):
                print("❌ Authentication identity mismatch.")
                return None

        print("✅ Supabase session created.")
        return user.get("role")

    except Exception as e:
        print("❌ Authentication error:", e)
        return None


# =========================================================
# GET USER
# =========================================================

def get_user(username):

    username = username.strip().lower()

    try:

        response: Any = (
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

        response: Any = (
            supabase
            .table("users")
            .select("connection_code")
            .eq("username", username)
            .execute()
        )

        if response.data:
            user_data: Any = response.data[0]
            return user_data.get("connection_code")

        return None

    except Exception as e:
        print("❌ Connection code error:", e)
        return None


# =========================================================
# VERIFY CONNECTION CODE
# =========================================================

def verify_connection_code(connection_code):

    if not connection_code:
        return False

    connection_code = connection_code.strip().upper()

    try:

        response: Any = (
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

    if not connection_code or not caregiver:
        return False

    connection_code = connection_code.strip().upper()
    caregiver = caregiver.strip().lower()

    try:
        # Find Senior using SECURITY DEFINER RPC
        response: Any = supabase.rpc(
            "get_senior_by_connection_code",
            {
                "p_connection_code": connection_code
            }
        ).execute()

        if not response.data:
            return False
        
        senior_data: Any = response.data[0]
        senior_username = senior_data.get("username")

        # Check caregiver
        caregiver_response: Any = (
            supabase
            .table("users")
            .select("username")
            .eq("username", caregiver)
            .eq("role", "Caregiver")
            .execute()
        )

        if not caregiver_response.data:
            return False

        # Check existing connection
        existing: Any = (
            supabase
            .table("connections")
            .select("id")
            .eq("senior_username", senior_username)
            .eq("caregiver_username", caregiver)
            .execute()
        )

        if existing.data:
            return True

        # Create connection
        supabase.table("connections").insert({
            "senior_username": senior_username,
            "caregiver_username": caregiver
        }).execute()

        return True

    except Exception as e:
        error_message = str(e).lower()
        if (
            "duplicate" in error_message
            or "already exists" in error_message
            or "unique constraint" in error_message
            or "23505" in error_message
        ):
            return True
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

        response: Any = (
            supabase
            .table("connections")
            .select("senior_username")
            .eq("caregiver_username", caregiver)
            .order("senior_username")
            .execute()
        )
        
        if not response.data:
            return []

        return [str(row.get("senior_username", "")) for row in response.data]

    except Exception as e:
        print("❌ Get seniors error:", e)
        return []


# =========================================================
# GET CONNECTED CAREGIVERS
# =========================================================

def get_connected_caregivers(senior):

    senior = str(senior).strip().lower()

    try:

        response: Any = (
            supabase
            .table("connections")
            .select("caregiver_username")
            .eq("senior_username", senior)
            .order("caregiver_username")
            .execute()
        )

        results = []
        
        if not response.data:
            return results

        for connection in response.data:
            
            conn_data: Any = connection
            caregiver_username = str(conn_data.get("caregiver_username", "")).strip()
            
            if not caregiver_username:
                continue

            caregiver_response: Any = (
                supabase
                .table("users")
                .select("full_name,username,email,mobile")
                .eq("username", caregiver_username)
                .execute()
            )

            if caregiver_response.data:
                
                c_user: Any = caregiver_response.data[0]
                
                results.append((
                    str(c_user.get("full_name", "")),
                    str(c_user.get("username", "")),
                    str(c_user.get("email", "")),
                    str(c_user.get("mobile", ""))
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

        response: Any = (
            supabase
            .table("users")
            .select("email")
            .eq("username", username)
            .execute()
        )

        if response.data:
            user_data: Any = response.data[0]
            return user_data.get("email")

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

        response: Any = (
            supabase
            .table("users")
            .select("mobile")
            .eq("username", username)
            .execute()
        )

        if response.data:
            user_data: Any = response.data[0]
            return user_data.get("mobile")

        return None

    except Exception as e:
        print("❌ Get mobile error:", e)
        return None