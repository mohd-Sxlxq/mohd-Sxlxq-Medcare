import streamlit as st
import matplotlib.pyplot as plt

from backend.user import (
    get_my_seniors,
    verify_connection_code,
    connect_caregiver_to_senior
)

from backend.storage import (
    get_last_7_records,
    get_latest_health,
    get_latest_risk
)

from backend.reminder import save_reminder


def show_caretaker_dashboard():

    st.title("👨‍⚕️ Caregiver Dashboard")
    st.write("Manage your seniors and monitor their health.")

    caretaker = st.session_state.username

    # =====================================================
    # CONNECT TO SENIOR
    # =====================================================

    st.subheader("🔗 Connect to a Senior")

    st.write(
        "Ask the Senior for their MedCare connection code "
        "and enter it below."
    )

    connection_code = st.text_input(
        "Senior Connection Code",
        placeholder="MC-SNR-XXXXXXXX",
        key="senior_connection_code"
    )

    if st.button(
        "Connect Senior",
        key="connect_senior"
    ):

        if not connection_code.strip():

            st.warning("Please enter the Senior connection code.")

        else:

            connection_code = connection_code.strip().upper()

            # Verify code first
            code_valid = verify_connection_code(
                connection_code
            )

            if not code_valid:

                st.error(
                    "❌ Invalid Senior connection code."
                )

            else:

                # Connect current caregiver
                result = connect_caregiver_to_senior(
                    connection_code,
                    caretaker
                )

                if result:

                    st.success(
                        "✅ Senior connected successfully!"
                    )

                    st.rerun()

                else:

                    st.error(
                        "❌ Unable to connect Senior."
                    )

    st.divider()

    # =====================================================
    # CONNECTED SENIORS
    # =====================================================

    seniors = get_my_seniors(caretaker)

    st.subheader("👥 Connected Seniors")

    if not seniors:

        st.info(
            "No seniors connected yet."
        )

        return

    for senior in seniors:

        bp, sugar, hr = get_latest_health(
            senior
        )

        risk = get_latest_risk(
            senior
        )

        st.markdown(
            f"### 🧓 {senior}"
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "❤️ BP",
            str(bp) if bp is not None else "--"
        )

        c2.metric(
            "🍬 Sugar",
            str(sugar) if sugar is not None else "--"
        )

        c3.metric(
            "💓 Heart",
            str(hr) if hr is not None else "--"
        )

        if risk == "High Risk":

            c4.error("🔴 High")

        elif risk == "Warning":

            c4.warning("🟡 Warning")

        elif risk:

            c4.success("🟢 Normal")

        else:

            c4.info("--")

        st.divider()

    # =====================================================
    # ADD MEDICATION REMINDER (WITH 90-DAY DURATION & TIME SLOTS)
    # =====================================================

    st.subheader("💊 Add Medication Schedule")

    selected_senior = st.selectbox(
        "Select Senior",
        seniors,
        key="selected_senior"
    )

    medicine = st.text_input(
        "Medicine Name",
        key="medicine"
    )

    # Generate hour and half-hour time slots (e.g., 08:00, 08:30, 09:00...)
    time_slots = []
    for h in range(24):
        time_slots.append(f"{h:02d}:00")
        time_slots.append(f"{h:02d}:30")

    col1, col2 = st.columns(2)

    with col1:
        start_slot = st.selectbox("Start Time", time_slots, index=16, key="start_slot") # Default 08:00

    with col2:
        end_slot = st.selectbox("End Time", time_slots, index=17, key="end_slot") # Default 08:30

    duration_days = st.slider(
        "Duration (Days - Auto-repeats daily up to 90 days)",
        min_value=1,
        max_value=90,
        value=7,
        key="duration_days"
    )

    if st.button(
        "Save Reminder Schedule",
        type="primary",
        key="add_reminder"
    ):

        if not medicine.strip():

            st.warning("Please enter a medicine name.")

        else:

            success = save_reminder(
                medicine=medicine.strip(),
                start_time=f"{start_slot}:00",
                end_time=f"{end_slot}:00",
                senior=selected_senior,
                duration_days=duration_days
            )

            if success:
                st.success(
                    f"✅ Successfully scheduled {medicine.strip()} for {duration_days} days!"
                )
                st.rerun()
            else:
                st.error("❌ Failed to save reminder to database.")

    st.divider()

    # =====================================================
    # HEALTH TRENDS
    # =====================================================

    st.subheader("📈 Health Trends")

    selected = st.selectbox(
        "Choose Senior",
        seniors,
        key="trend_senior"
    )

    records = get_last_7_records(
        selected
    )

    if records.empty:

        st.info(
            "No health records found."
        )

        return

    records = (
        records
        .iloc[::-1]
        .reset_index(drop=True)
    )

    records["Label"] = (
        records["Date"]
        + "\n"
        + records["Time"]
    )

    # =====================================================
    # BLOOD PRESSURE
    # =====================================================

    st.write("### ❤️ Blood Pressure")

    fig = plt.figure(
        figsize=(8, 4)
    )

    plt.plot(
        records["Label"],
        records["Blood Pressure"],
        marker="o"
    )

    plt.xticks(
        rotation=45
    )

    plt.grid(True)

    plt.tight_layout()

    st.pyplot(fig)

    # =====================================================
    # SUGAR
    # =====================================================

    st.write("### 🍬 Sugar Level")

    fig = plt.figure(
        figsize=(8, 4)
    )

    plt.plot(
        records["Label"],
        records["Sugar Level"],
        marker="o"
    )

    plt.xticks(
        rotation=45
    )

    plt.grid(True)

    plt.tight_layout()

    st.pyplot(fig)

    # =====================================================
    # HEART RATE
    # =====================================================

    st.write("### 💓 Heart Rate")

    fig = plt.figure(
        figsize=(8, 4)
    )

    plt.plot(
        records["Label"],
        records["Heart Rate"],
        marker="o"
    )

    plt.xticks(
        rotation=45
    )

    plt.grid(True)

    plt.tight_layout()

    st.pyplot(fig)

    # =====================================================
    # RISK HISTORY
    # =====================================================

    st.write("### 🚨 Risk History")

    st.dataframe(
        records[
            [
                "Date",
                "Time",
                "Risk Level"
            ]
        ],
        use_container_width=True
    )