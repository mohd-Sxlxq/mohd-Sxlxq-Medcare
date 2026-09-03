import hashlib
import random
import string
from typing import cast, Any, List, Dict

from backend.supabase_client import supabase


# =========================================================
# PASSWORD HASH
# =========================================================

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# =========================================================
# GENERATE SENIOR CONNECTION CODE
# =========================================================

def generate_connection_code() -> str | None:

    while True:

        code = "MC-SNR-" + "".join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=8
            )
        )

        try:

            response = (
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
    full_name: str,
    username: str,
    password: str,
    role: str,
    email: str,
    mobile: str,
    address: str = ""
):

    username = username.strip().lower()
    real_email = email.strip().lower()
    role = role.strip().title()

    try:
        response = (
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

    system_auth_email = f"{username}@medcare-system.local"

    try:
        try:
            auth_response = supabase.auth.sign_up({
                "email": system_auth_email,
                "password": password
            }) # type: ignore
            
            if not auth_response.user:
                return False, "Supabase Auth registration failed."
                
            auth_id = str(auth_response.user.id) # type: ignore
            
        except Exception as auth_e:
            auth_error_msg = str(auth_e).lower()
            if "already registered" in auth_error_msg or "already exists" in auth_error_msg:
                try:
                    recover_response = supabase.auth.sign_in_with_password({
                        "email": system_auth_email,
                        "password": password
                    }) # type: ignore
                    
                    if recover_response.user:
                        auth_id = str(recover_response.user.id) # type: ignore
                    else:
                        raise Exception("Recovery failed")
                except Exception:
                    return False, "This username is permanently locked by a previous password mismatch. Please choose a new username."
            else:
                raise auth_e

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

def authenticate_user(username: str, password: str):

    username = username.strip().lower()
    system_auth_email = f"{username}@medcare-system.local"

    try:
        response = (
            supabase
            .table("users")
            .select("*")
            .eq("username", username)
            .execute()
        )

        data = cast(List[Dict[str, Any]], response.data)

        if not data:
            print("❌ User not found.")
            return None

        user = data[0]
        stored_real_email = str(user.get("email", ""))

        try:
            auth_response = supabase.auth.sign_in_with_password({
                "email": system_auth_email,
                "password": password
            }) # type: ignore
        except Exception:
            auth_response = supabase.auth.sign_in_with_password({
                "email": stored_real_email,
                "password": password
            }) # type: ignore

        if not auth_response.user:
            print("❌ Supabase login failed.")
            return None

        if user.get("auth_id"):
            if str(auth_response.user.id) != str(user["auth_id"]): # type: ignore
                print("❌ Authentication identity mismatch.")
                return None

        print("✅ Supabase session created.")
        return str(user["role"])

    except Exception as e:
        print("❌ Authentication error:", e)
        return None


# =========================================================
# GET USER
# =========================================================

def get_user(username: str):

    username = username.strip().lower()

    try:
        response = (
            supabase
            .table("users")
            .select("*")
            .eq("username", username)
            .execute()
        )

        data = cast(List[Dict[str, Any]], response.data)

        if data:
            return data[0]

        return None

    except Exception as e:
        print("❌ Get user error:", e)
        return None


# =========================================================
# GET CONNECTION CODE
# =========================================================

def get_connection_code(username: str):

    username = username.strip().lower()

    try:
        response = (
            supabase
            .table("users")
            .select("connection_code")
            .eq("username", username)
            .execute()
        )

        data = cast(List[Dict[str, Any]], response.data)

        if data:
            return str(data[0]["connection_code"])

        return None

    except Exception as e:
        print("❌ Connection code error:", e)
        return None


# =========================================================
# VERIFY CONNECTION CODE
# =========================================================

def verify_connection_code(connection_code: str):

    if not connection_code:
        return False

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
    connection_code: str,
    caregiver: str
):

    if not connection_code or not caregiver:
        return False

    connection_code = connection_code.strip().upper()
    caregiver = caregiver.strip().lower()

    try:
        response = supabase.rpc(
            "get_senior_by_connection_code",
            {
                "p_connection_code": connection_code
            }
        ).execute()

        data = cast(List[Dict[str, Any]], response.data)

        if not data:
            return False

        senior_username = str(data[0]["username"])

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

        existing = (
            supabase
            .table("connections")
            .select("id")
            .eq("senior_username", senior_username)
            .eq("caregiver_username", caregiver)
            .execute()
        )

        if existing.data:
            return True

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
    caregiver_username: str,
    connection_code: str
):

    return connect_caregiver_to_senior(
        connection_code,
        caregiver_username
    )


# =========================================================
# GET MY SENIORS
# =========================================================

def get_my_seniors(caregiver: str):

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
        
        data = cast(List[Dict[str, Any]], response.data)
        return [str(row["senior_username"]) for row in data]

    except Exception as e:
        print("❌ Get seniors error:", e)
        return []


# =========================================================
# GET CONNECTED CAREGIVERS
# =========================================================

def get_connected_caregivers(senior: str):

    senior = senior.strip().lower()

    try:
        response = (
            supabase
            .table("connections")
            .select("caregiver_username")
            .eq("senior_username", senior)
            .order("caregiver_username")
            .execute()
        )
        
        data = cast(List[Dict[str, Any]], response.data)
        results = []

        for connection in data:
            caregiver_username = str(connection["caregiver_username"])

            caregiver_response = (
                supabase
                .table("users")
                .select("full_name,username,email,mobile")
                .eq("username", caregiver_username)
                .execute()
            )
            
            cg_data = cast(List[Dict[str, Any]], caregiver_response.data)

            if cg_data:
                cg = cg_data[0]
                results.append((
                    str(cg["full_name"]),
                    str(cg["username"]),
                    str(cg["email"]),
                    str(cg["mobile"])
                ))

        return results

    except Exception as e:
        print("❌ Get caregivers error:", e)
        return []


# =========================================================
# GET USER EMAIL
# =========================================================

def get_user_email(username: str):

    username = username.strip().lower()

    try:
        response = (
            supabase
            .table("users")
            .select("email")
            .eq("username", username)
            .execute()
        )
        
        data = cast(List[Dict[str, Any]], response.data)

        if data:
            return str(data[0]["email"])

        return None

    except Exception as e:
        print("❌ Get email error:", e)
        return None


# =========================================================
# GET USER MOBILE
# =========================================================

def get_user_mobile(username: str):

    username = username.strip().lower()

    try:
        response = (
            supabase
            .table("users")
            .select("mobile")
            .eq("username", username)
            .execute()
        )
        
        data = cast(List[Dict[str, Any]], response.data)

        if data:
            return str(data[0]["mobile"])

        return None

    except Exception as e:
        print("❌ Get mobile error:", e)
        return None