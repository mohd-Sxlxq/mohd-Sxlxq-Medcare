import streamlit as st
from frontend.auth import show_auth
from frontend.senior_dash import show_senior_dashboard
from frontend.caretaker_dash import show_caretaker_dashboard

st.set_page_config(
    page_title="MedCare",
    page_icon="💙",
    layout="wide"
)

st.markdown("""
<style>
.main{
    background-color:#f4f8ff;
}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = ""

if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.logged_in:

    show_auth()

else:

    with st.sidebar:

        st.title("💙 MedCare")
        st.write(f"👤 {st.session_state.username}")
        st.write(f"Role : {st.session_state.role}")

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.role = ""
            st.session_state.username = ""
            st.rerun()

    if st.session_state.role == "Senior":
        show_senior_dashboard()

    elif st.session_state.role == "Caregiver":
        show_caretaker_dashboard()