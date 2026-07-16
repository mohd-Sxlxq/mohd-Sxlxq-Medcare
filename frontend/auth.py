import streamlit as st

from backend.user import (
    create_user,
    authenticate_user,
    verify_connection_code,
    connect_caregiver
)


def show_auth():

    st.markdown("""
    <style>

    .main{
        background:#f4f8ff;
    }

    .block-container{
        max-width:550px;
        margin:auto;
        padding-top:40px;
    }

    .stButton>button{
        width:100%;
        height:45px;
        border-radius:10px;
        background:#2c7be5;
        color:white;
        font-weight:bold;
    }

    </style>
    """, unsafe_allow_html=True)

    st.title("💙 MedCare")

    menu = st.radio(
        "",
        ["Login", "Signup"],
        horizontal=True,
        key="auth_menu"
    )

    # ==========================================================
    # LOGIN
    # ==========================================================

    if menu == "Login":

        username = st.text_input(
            "Username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            key="login_button"
        ):

            if username.strip() == "" or password.strip() == "":
                st.warning("Please enter username and password.")
                return

            role = authenticate_user(
                username,
                password
            )

            if role:

                st.session_state.logged_in = True
                st.session_state.username = username.lower()
                st.session_state.role = role

                st.success("Login Successful")
                st.rerun()

            else:

                st.error("Invalid Username or Password.")

    # ==========================================================
    # SIGNUP
    # ==========================================================

    else:

        full_name = st.text_input(
            "Full Name",
            key="signup_fullname"
        )

        email = st.text_input(
            "Email Address",
            key="signup_email"
        )

        mobile = st.text_input(
            "Mobile Number",
            key="signup_mobile"
        )

        role = st.selectbox(
            "Select Role",
            ["Senior", "Caregiver"],
            key="signup_role"
        )

        address = ""
        connection_code = ""

        if role == "Senior":

            address = st.text_area(
                "Permanent Address",
                key="signup_address"
            )

        else:

            connection_code = st.text_input(
                "Senior Connection Code",
                key="signup_connection_code"
            )

        username = st.text_input(
            "Username",
            key="signup_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        confirm = st.text_input(
            "Confirm Password",
            type="password",
            key="signup_confirm"
        )

        if st.button(
            "Create Account",
            key="signup_button"
        ):

            if (
                full_name.strip() == "" or
                email.strip() == "" or
                mobile.strip() == "" or
                username.strip() == "" or
                password.strip() == ""
            ):
                st.warning("Please fill all required fields.")
                return

            if password != confirm:
                st.error("Passwords do not match.")
                return

            if role == "Senior":

                if address.strip() == "":
                    st.warning("Please enter your permanent address.")
                    return

            else:

                if connection_code.strip() == "":
                    st.warning("Please enter Senior Connection Code.")
                    return

                if not verify_connection_code(connection_code):
                    st.error("Invalid Senior Connection Code.")
                    return

            success = create_user(
                full_name,
                username,
                password,
                role,
                email,
                mobile,
                address
            )

            if not success:
                st.error("Username already exists.")
                return

            if role == "Caregiver":

                connect_caregiver(
                    username,
                    connection_code
                )

            st.success("Account created successfully.")
            st.info("Please login to continue.")