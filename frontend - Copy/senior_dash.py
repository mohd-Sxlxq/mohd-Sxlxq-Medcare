import streamlit as st
import requests
from datetime import datetime
from backend.user import (
    get_connection_code,
    get_connected_caregivers
)
from backend.storage import (
    get_latest_health,
    get_last_7_records
)

from backend.reminder import (
    get_reminders_for_senior,
    mark_taken,
    mark_notified
)

from backend.mail import send_missed_med_alert


def show_senior_dashboard():

    st.title("🧓 Senior Dashboard")
    st.write("Welcome to MedCare")
    st.subheader("🔗 Your Connection Code")

    code = get_connection_code(
        st.session_state.username
    )

    st.code(code)

    st.info(
    "Share this code with your caregiver to connect."
    )
    

    # ================= HEALTH INPUT =================

    st.subheader("🩺 Enter Health Details")

    bp = st.number_input(
        "Blood Pressure",
        min_value=0.0
    )   

    sugar = st.number_input(
        "Sugar Level",
        min_value=0.0
    )

    hr = st.number_input(
        "Heart Rate",
        min_value=0.0
    )

    if st.button("Check Health"):

        response = requests.post(
            "http://127.0.0.1:8000/submit-health",
            params={
                "senior": st.session_state.username,
                "bp": bp,
                "sugar": sugar,
                "hr": hr
            }
        )

        if response.status_code == 200:

            risk = response.json()["risk_level"]

            if risk == "High Risk":
                st.error("⚠ High Risk Detected")

            elif risk == "Warning":
                st.warning("⚠ Warning")

            else:
                st.success("✅ Your Health is Normal")

        else:
            st.error("Unable to connect to server.")

    st.divider()

    # ================= LATEST HEALTH =================

    st.subheader("❤️ Latest Health Status")

    bp, sugar, hr = get_latest_health(
        st.session_state.username
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Blood Pressure",
        bp if bp is not None else "--"
    )

    c2.metric(
        "Sugar Level",
        sugar if sugar is not None else "--"
    )

    c3.metric(
        "Heart Rate",
        hr if hr is not None else "--"
    )

    st.divider()

    # ================= HISTORY =================

    st.subheader("📋 Recent Health Records")

    history = get_last_7_records(
        st.session_state.username
    )

    if history.empty:
        st.info("No records available.")
    else:
        st.dataframe(
            history,
            use_container_width=True
        )

    st.divider()

    # ================= MEDICATION =================

    st.subheader("💊❤️ Medication Reminder")

    reminders = get_reminders_for_senior(
        st.session_state.username
    )

    if reminders.empty:
        st.info("No medication reminders.")
        return

    now = datetime.now().time()

    for _, row in reminders.iterrows():

        reminder_id = row["id"]

        st.write(
            f"💊 **{row['Medicine']}**"
        )

        st.write(
            f"🕒 {row['Start']} - {row['End']}"
        )

        start = datetime.strptime(
            str(row["Start"]),
            "%H:%M:%S"
        ).time()

        end = datetime.strptime(
            str(row["End"]),
            "%H:%M:%S"
        ).time()

        if row["Taken"] == "No":

            if start <= now <= end:

                if st.button(
                    f"Mark Taken - {row['Medicine']}",
                    key=f"taken_{reminder_id}"
                ):

                    mark_taken(reminder_id)

                    st.success(
                        "Medicine marked as taken."
                    )

                    st.rerun()

            elif now > end:

                if row["Notified"] == "No":

                    send_missed_med_alert(
                        st.session_state.username,
                        row["Medicine"]
                    )

                    mark_notified(reminder_id)

                    st.error(
                        "Medication missed. Caregiver notified."
                    )

                else:

                    st.error(
                        "Medication missed."
                    )

            else:

                st.info(
                    "Not time yet."
                )

        else:

            st.success(
                "✅ Medicine Taken"
            )