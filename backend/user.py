import hashlib
import random
import string

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
) -> tuple[bool, str]:

    username = username.strip().lower()
    email = email.strip().lower()
    role = role.strip().title()

    try:
        # Check if username already exists in our table
        response = (
            supabase
            .table("users")
            .select("id")
            .eq("username", username)
            .execute()
        )

        if response.data:
            return False, "This username is already taken. Please choose another."

    except Exception as e:
        print("❌ Username check error:", e)
        return False, "Database connection error while checking username."

    connection_code = None

    if role == "Senior":
        connection_code = generate_connection_code()

        if connection_code is None:
            return False, "Failed to generate connection code."

    try:
        # Create Supabase Auth account
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        if not auth_response.user:
            return False, "Supabase Auth registration failed."

        auth_id = str(auth_response.user.id)

        # Create MedCare profile
        supabase.table("users").insert({
            "full_name": full_name.strip(),
            "username": username,
            "password": hash_password(password),
            "role": role,
            "email": email,
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
        
        # Translate database errors into human-readable messages
        if "users_username_key" in error_msg:
            return False, "This username is already taken. Please choose another."
        if "users_email_key" in error_msg or "already registered" in error_msg.lower():
            return False, "This email address is already registered."
        if "characters" in error_msg.lower() or "password" in error_msg.lower():
            return False, "Password must be at least 6 characters long."
            
        return False, "Registration failed. Please check your details and try again."


# =========================================================
# LOGIN
# =========================================================

def authenticate_user(username: str, password: str) -> str | None:

    username = username.strip().lower()

    try:

        response = supabase.rpc(
            "get_login_user",
            {
                "p_username": username
            }
        ).execute()

        if not response.data:

            print("❌ User not found.")
            return None

        # Cast to dict and tell the linter to ignore this specific line
        user_data = dict(response.data[0])  # type: ignore

        email = str(user_data.get("email"))

        # Pass the credentials as a variable and ignore the strict type check
        credentials = {"email": email, "password": password}
        auth_response = supabase.auth.sign_in_with_password(credentials)  # type: ignore

        if not auth_response.user:
            
            print("❌ Supabase login failed.")
            return None

        # Verify Auth ID
        stored_auth_id = user_data.get("auth_id")  # type: ignore
        if stored_auth_id:
            
            if str(auth_response.user.id) != str(stored_auth_id):  # type: ignore
                
                print("❌ Authentication identity mismatch.")
                return None

        print("✅ Supabase session created.")
    except Exception as e:

        print("❌ Authentication error:", e)
        return None


# =========================================================
# GET USER
# =========================================================

def get_user(username: str) -> dict | None:

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

            return response.data[0]  # type: ignore

        return None

    except Exception as e:

        print("❌ Get user error:", e)
        return None


# =========================================================
# GET CONNECTION CODE
# =========================================================

def get_connection_code(username: str) -> str | None:

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

            return response.data[0]["connection_code"]  # type: ignore

        return None

    except Exception as e:

        print("❌ Connection code error:", e)
        return None


# =========================================================
# VERIFY CONNECTION CODE
# =========================================================

def verify_connection_code(connection_code: str) -> bool:

    if not connection_code:

        print("❌ Connection code is empty.")
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
) -> bool:

    if not connection_code:

        print("❌ Connection code is empty.")
        return False

    if not caregiver:

        print("❌ Caregiver username is empty.")
        return False

    connection_code = connection_code.strip().upper()
    caregiver = caregiver.strip().lower()

    try:

        # -------------------------------------------------
        # Find Senior using SECURITY DEFINER RPC
        # -------------------------------------------------

        response = supabase.rpc(
            "get_senior_by_connection_code",
            {
                "p_connection_code": connection_code
            }
        ).execute()

        if not response.data:

            print("❌ Senior not found.")
            return False

        senior_username = response.data[0]["username"]  # type: ignore

        # -------------------------------------------------
        # Check caregiver
        # -------------------------------------------------

        caregiver_response = (
            supabase
            .table("users")
            .select("username")
            .eq("username", caregiver)
            .eq("role", "Caregiver")
            .execute()
        )

        if not caregiver_response.data:

            print("❌ Caregiver not found.")
            return False

        # -------------------------------------------------
        # Check existing connection
        # -------------------------------------------------

        existing = (
            supabase
            .table("connections")
            .select("id")
            .eq("senior_username", senior_username)
            .eq("caregiver_username", caregiver)
            .execute()
        )

        if existing.data:

            print("✅ Caregiver is already connected to this Senior.")
            return True

        # -------------------------------------------------
        # Create connection
        # -------------------------------------------------

        supabase.table("connections").insert({

            "senior_username": senior_username,
            "caregiver_username": caregiver

        }).execute()

        print("✅ Caregiver connected to Senior.")

        return True

    except Exception as e:

        error_message = str(e).lower()

        if (
            "duplicate" in error_message
            or "already exists" in error_message
            or "unique constraint" in error_message
            or "23505" in error_message
        ):

            print("✅ Caregiver is already connected to this Senior.")
            return True

        print("❌ Caregiver connection error:", repr(e))

        return False


# =========================================================
# CONNECT CAREGIVER
# =========================================================

def connect_caregiver(
    caregiver_username: str,
    connection_code: str
) -> bool:

    return connect_caregiver_to_senior(
        connection_code,
        caregiver_username
    )


# =========================================================
# GET MY SENIORS
# =========================================================

def get_my_seniors(caregiver: str) -> list[str]:

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

            str(row["senior_username"])

            for row in response.data  # type: ignore

        ]

    except Exception as e:

        print("❌ Get seniors error:", e)
        return []


# =========================================================
# GET CONNECTED CAREGIVERS
# =========================================================

def get_connected_caregivers(senior: str) -> list[tuple[str, str, str, str]]:

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

        results = []

        for connection in response.data:  # type: ignore

            caregiver_username = connection[
                "caregiver_username"
            ]

            caregiver_response = (
                supabase
                .table("users")
                .select(
                    "full_name,username,email,mobile"
                )
                .eq(
                    "username",
                    caregiver_username
                )
                .execute()
            )

            if caregiver_response.data:

                caregiver = caregiver_response.data[0]  # type: ignore

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

def get_user_email(username: str) -> str | None:

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

            return response.data[0]["email"]  # type: ignore

        return None

    except Exception as e:

        print("❌ Get email error:", e)
        return None


# =========================================================
# GET USER MOBILE
# =========================================================

def get_user_mobile(username: str) -> str | None:

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

            return response.data[0]["mobile"]  # type: ignore

        return None

    except Exception as e:

        print("❌ Get mobile error:", e)
        return None