import streamlit as st
import matplotlib.pyplot as plt

from backend.user import get_my_seniors

from backend.storage import (
    get_last_7_records,
    get_latest_health,
    get_latest_risk
)

from backend.reminder import (
    save_reminder,
    get_reminders_for_senior
)


def show_caretaker_dashboard():

    st.title("👨‍⚕️ Caregiver Dashboard")
    st.write("Manage your seniors and monitor their health.")

    caretaker = st.session_state.username

    seniors = get_my_seniors(caretaker)

    # =====================================================
    # CONNECTED SENIORS
    # =====================================================

    st.subheader("👥 Connected Seniors")

    if not seniors:

        st.info(
            "No seniors connected yet. Ensure you entered a "
            "valid Senior Connection Code during registration."
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
            bp if bp is not None else "--"
        )

        c2.metric(
            "🍬 Sugar",
            sugar if sugar is not None else "--"
        )

        c3.metric(
            "💓 Heart",
            hr if hr is not None else "--"
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
    # ADD MEDICATION REMINDER
    # =====================================================

    st.subheader("💊 Add Medication Reminder")
    st.write("Schedule medicines individually with a custom duration.")

    selected_senior = st.selectbox(
        "Select Senior",
        seniors,
        key="selected_senior"
    )

    medicine = st.text_input(
        "Medicine Name",
        placeholder="e.g., Aspirin",
        key="med_name_input"
    )

    # Easy Slider for 1 to 90 days selection
    duration = st.slider(
        "🗓️ Duration (Days)",
        min_value=1,
        max_value=90,
        value=30,
        help="Slide to select how many days this medication plan should last."
    )

    # Generate time options in 30-minute intervals
    time_labels = []
    time_values = []
    for h in range(24):
        for m in (0, 30):
            ampm = "AM" if h < 12 else "PM"
            dh = 12 if h == 0 else (h - 12 if h > 12 else h)
            time_labels.append(f"{dh}:{m:02d} {ampm}")
            time_values.append(f"{h:02d}:{m:02d}:00")

    col1, col2 = st.columns(2)

    with col1:
        # Default Start Time: 8:00 AM (Index 16)
        start_label = st.selectbox("Start Time", time_labels, index=16)
        start_idx = time_labels.index(start_label)

    with col2:
        # End Time dynamically defaults to +90 minutes (3 steps of 30 mins)
        default_end_idx = (start_idx + 3) % 48
        end_label = st.selectbox("End Time", time_labels, index=default_end_idx)

    if st.button("Save Medication", type="primary", use_container_width=True):

        if not medicine.strip():
            st.warning("Please enter a medicine name.")
        else:
            start_val = time_values[time_labels.index(start_label)]
            end_val = time_values[time_labels.index(end_label)]

            saved = save_reminder(
                medicine.strip(),
                start_val,
                end_val,
                selected_senior
            )
            
            if saved:
                st.success(f"✅ '{medicine.strip()}' scheduled for {duration} days from {start_label} to {end_label}!")
            else:
                st.error("❌ Failed to save medication.")
                
    st.divider()

    # =====================================================
    # MEDICATION TRACKER
    # =====================================================
    
    st.subheader("📋 Medication Status")
    
    track_senior = st.selectbox(
        "Select Senior to View Medications",
        seniors,
        key="track_senior"
    )
    
    reminders_df = get_reminders_for_senior(track_senior)
    
    if reminders_df.empty:
        st.info(f"No medications scheduled for {track_senior}.")
    else:
        st.dataframe(
            reminders_df[["Medicine", "Start", "End", "Taken"]],
            use_container_width=True
        )

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