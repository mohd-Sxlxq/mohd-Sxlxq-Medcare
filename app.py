import streamlit as st

from backend.user import authenticate_user, create_user
from frontend.senior_dash import show_senior_dashboard
from frontend.caretaker_dash import show_caretaker_dashboard

# Page Configuration
st.set_page_config(
    page_title="MedCare System",
    page_icon="🩺",
    layout="wide"
)

# =========================================================
# SESSION STATE INITIALIZATION
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = ""


# =========================================================
# AUTHENTICATION PAGE (CLASSIC LAYOUT)
# =========================================================

def show_auth_page():
    st.title("🩺 MedCare System")
    st.write("Your intelligent senior health and medication monitoring companion.")

    auth_mode = st.radio("Choose Action", ["Login", "Create Account"], horizontal=True)

    st.divider()

    if auth_mode == "Login":
        st.subheader("🔑 Login to your account")

        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login", type="primary", use_container_width=True):
            if not login_username.strip() or not login_password.strip():
                st.warning("Please fill in all fields.")
            else:
                role = authenticate_user(login_username, login_password)

                if role:
                    st.session_state.logged_in = True
                    st.session_state.role = role
                    st.session_state.username = login_username.strip().lower()
                    st.success(f"✅ Welcome back, {login_username}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password.")

    else:
        st.subheader("📝 Create a new MedCare account")

        new_name = st.text_input("Full Name", key="signup_name")
        new_username = st.text_input("Choose Username", key="signup_user")
        new_password = st.text_input("Choose Password (min 6 chars)", type="password", key="signup_pass")
        new_role = st.selectbox("Select Role", ["Senior", "Caregiver"], key="signup_role")
        new_email = st.text_input("Email (for notifications)", key="signup_email")
        new_mobile = st.text_input("Mobile Number", key="signup_mobile")
        new_address = st.text_area("Address (Optional)", key="signup_address")

        if st.button("Register Account", type="primary", use_container_width=True):
            if not new_name or not new_username or not new_password or not new_email or not new_mobile:
                st.warning("Please fill in all required fields.")
            else:
                success, message = create_user(
                    full_name=new_name,
                    username=new_username,
                    password=new_password,
                    role=new_role,
                    email=new_email,
                    mobile=new_mobile,
                    address=new_address
                )

                if success:
                    st.success("✅ Account created successfully! Switch to 'Login' above to sign in.")
                else:
                    st.error(f"❌ {message}")


# =========================================================
# MAIN APP ROUTER
# =========================================================

def main():
    if not st.session_state.logged_in:
        show_auth_page()
    else:
        # Sidebar logout button for convenience
        with st.sidebar:
            st.write(f"Logged in as: **{st.session_state.username}**")
            st.write(f"Role: **{st.session_state.role}**")
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.role = None
                st.session_state.username = ""
                st.rerun()

        # Route directly to the appropriate dashboard
        if st.session_state.role == "Senior":
            show_senior_dashboard()
        elif st.session_state.role == "Caregiver":
            show_caretaker_dashboard()
        else:
            st.error("❌ Unknown user role detected.")


if __name__ == "__main__":
    main()