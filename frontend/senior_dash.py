import streamlit as st
from datetime import datetime

from backend.user import (
    get_connection_code,
    get_connected_caregivers,
)

from backend.storage import (
    save_health_record,
    get_latest_health,
    get_last_7_records,
)

from backend.reminder import (
    get_reminders_for_senior,
    mark_taken,
    mark_notified,
)

from backend.mail import (
    send_missed_med_alert,
    send_email_alert,
)


def show_senior_dashboard():

    st.title("🧓 Senior Dashboard")
    st.write(f"Welcome, **{st.session_state.username}**")

    # =====================================================
    # CONNECTION CODE
    # =====================================================

    st.subheader("🔗 Caregiver Connection")

    connection_code = get_connection_code(
        st.session_state.username
    )

    if connection_code:
        st.code(connection_code)
        st.info(
            "Share this connection code with your caregiver."
        )
    else:
        st.warning("Connection code is not available.")

    # =====================================================
    # CONNECTED CAREGIVERS
    # =====================================================

    caregivers = get_connected_caregivers(
        st.session_state.username
    )

    st.subheader("👨‍⚕️ Connected Caregivers")

    if not caregivers:
        st.info("No caregiver connected yet.")
    else:
        for caregiver in caregivers:
            if isinstance(caregiver, (tuple, list)):
                full_name = caregiver[0] if len(caregiver) > 0 else ""
                username = caregiver[1] if len(caregiver) > 1 else ""
                email = caregiver[2] if len(caregiver) > 2 else ""
                mobile = caregiver[3] if len(caregiver) > 3 else ""

                st.success(
                    f"👨‍⚕️ **{full_name}**\n\n"
                    f"Username: {username}\n\n"
                    f"Email: {email}\n\n"
                    f"Mobile: {mobile}"
                )
            else:
                st.success(f"👨‍⚕️ {caregiver}")

    st.divider()

    # =====================================================
    # HEALTH INPUT
    # =====================================================

    st.subheader("🩺 Enter Health Details")

    col1, col2, col3 = st.columns(3)

    with col1:
        bp = st.number_input(
            "Blood Pressure",
            min_value=0.0,
            max_value=400.0,
            value=120.0,
            step=1.0,
        )

    with col2:
        sugar = st.number_input(
            "Sugar Level",
            min_value=0.0,
            max_value=1000.0,
            value=100.0,
            step=1.0,
        )

    with col3:
        hr = st.number_input(
            "Heart Rate",
            min_value=0.0,
            max_value=300.0,
            value=75.0,
            step=1.0,
        )

    if st.button(
        "🩺 Check Health",
        type="primary",
        use_container_width=True,
    ):

        # Risk calculation
        if bp > 160 or sugar > 250 or hr > 120:
            risk = "High Risk"
        elif bp > 140 or sugar > 180 or hr > 100:
            risk = "Warning"
        else:
            risk = "Normal"

        # Save directly to Supabase
        saved = save_health_record(
            st.session_state.username,
            bp,
            sugar,
            hr,
            risk,
        )

        if saved:
            if risk == "High Risk":
                st.error("⚠️ High Risk Detected")
                
                # Trigger email alert directly (Cloud Fix)
                try:
                    send_email_alert(
                        st.session_state.username,
                        bp,
                        sugar,
                        hr,
                        risk
                    )
                except Exception as e:
                    print("Email Alert Error:", e)

            elif risk == "Warning":
                st.warning(
                    "⚠️ Warning: Please monitor your health."
                )
            else:
                st.success("✅ Your Health is Normal")

            st.success(
                "✅ Health record saved successfully."
            )

            st.rerun()

        else:
            st.error("❌ Unable to save health record.")

    st.divider()

    # =====================================================
    # LATEST HEALTH
    # =====================================================

    st.subheader("❤️ Latest Health Status")

    latest_bp, latest_sugar, latest_hr = get_latest_health(
        st.session_state.username
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "❤️ Blood Pressure",
            latest_bp if latest_bp is not None else "--",
        )

    with c2:
        st.metric(
            "🍬 Sugar Level",
            latest_sugar if latest_sugar is not None else "--",
        )

    with c3:
        st.metric(
            "💓 Heart Rate",
            latest_hr if latest_hr is not None else "--",
        )

    st.divider()

    # =====================================================
    # HEALTH HISTORY
    # =====================================================

    st.subheader("📋 Recent Health Records")

    history = get_last_7_records(
        st.session_state.username
    )

    if history.empty:
        st.info("No health records available yet.")
    else:
        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    # =====================================================
    # MEDICATION REMINDERS
    # =====================================================

    st.subheader("💊 Medication Reminders")

    reminders = get_reminders_for_senior(
        st.session_state.username
    )

    if reminders.empty:
        st.info("No medication reminders.")
        return

    now = datetime.now().time()

    for _, row in reminders.iterrows():

        reminder_id = row["id"]
        medicine = row["Medicine"]
        start_value = row["Start"]
        end_value = row["End"]

        st.markdown(f"### 💊 {medicine}")
        st.write(
            f"🕒 **{start_value} - {end_value}**"
        )

        try:
            start = datetime.strptime(
                str(start_value),
                "%H:%M:%S",
            ).time()

            end = datetime.strptime(
                str(end_value),
                "%H:%M:%S",
            ).time()

        except ValueError:
            st.warning(
                f"Invalid reminder time for {medicine}."
            )
            continue

        taken = str(row["Taken"]).strip().lower()
        notified = str(row["Notified"]).strip().lower()

        if taken == "no":

            # Medication window is active
            if start <= now <= end:

                if st.button(
                    f"✅ Mark {medicine} as Taken",
                    key=f"taken_{reminder_id}",
                    use_container_width=True,
                ):

                    result = mark_taken(reminder_id)

                    if result:
                        st.success(
                            f"✅ {medicine} marked as taken."
                        )
                        st.rerun()
                    else:
                        st.error(
                            "❌ Unable to update medication."
                        )

            # Medication window has ended
            elif now > end:

                if notified == "no":

                    alert_sent = send_missed_med_alert(
                        st.session_state.username,
                        medicine,
                    )

                    mark_notified(reminder_id)

                    if alert_sent:
                        st.error(
                            f"🚨 {medicine} was missed. "
                            "Caregiver notified."
                        )
                    else:
                        st.warning(
                            f"⚠️ {medicine} was missed. "
                            "Caregiver notification could not be sent."
                        )

                else:
                    st.error(
                        f"🚨 {medicine} was missed."
                    )

            # Medication window has not started
            else:
                st.info(
                    f"⏳ It is not time to take "
                    f"{medicine} yet."
                )

        else:
            st.success(
                f"✅ {medicine} — Medicine Taken"
            )

        st.divider()