import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime

from backend.user import get_my_seniors

from backend.storage import (
    get_last_7_records,
    get_latest_health,
    get_latest_risk
)

from backend.reminder import (
    save_reminder,
    get_reminders_for_senior,
    update_reminder,
    delete_reminder
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
    # ADD MEDICATION REMINDER (CREATE)
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
        start_label = st.selectbox("Start Time", time_labels, index=16)
        start_idx = time_labels.index(start_label)

    with col2:
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
    # MEDICATION TRACKER (READ)
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
    # MANAGE MEDICATIONS (UPDATE & DELETE)
    # =====================================================

    st.subheader("⚙️ Manage Scheduled Medications")
    
    manage_senior = st.selectbox(
        "Select Senior to Manage",
        seniors,
        key="manage_senior"
    )

    manage_df = get_reminders_for_senior(manage_senior)

    if manage_df.empty:
        st.info(f"No medications scheduled to manage for {manage_senior}.")
    else:
        # Create a dictionary of current reminders for easy selection
        med_options = {}
        for _, row in manage_df.iterrows():
            label = f"{row['Medicine']} ({row['Start']} to {row['End']})"
            med_options[label] = row

        selected_med_label = st.selectbox(
            "Select Medication to Edit or Delete", 
            list(med_options.keys())
        )
        
        selected_row = med_options[selected_med_label]
        rem_id = selected_row["id"]

        edit_med = st.text_input(
            "Edit Medicine Name", 
            value=selected_row["Medicine"],
            key="edit_med_input"
        )
        
        try:
            cur_start = datetime.strptime(str(selected_row["Start"]), "%H:%M:%S").time()
            cur_end = datetime.strptime(str(selected_row["End"]), "%H:%M:%S").time()
        except ValueError:
            cur_start = datetime.strptime("08:00:00", "%H:%M:%S").time()
            cur_end = datetime.strptime("09:30:00", "%H:%M:%S").time()

        c1, c2 = st.columns(2)
        with c1:
            edit_start = st.time_input("Edit Start Time", value=cur_start, key="edit_start")
        with c2:
            edit_end = st.time_input("Edit End Time", value=cur_end, key="edit_end")

        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("💾 Update Medication", type="primary", use_container_width=True):
                if not edit_med or not str(edit_med).strip():
                    st.warning("Medicine name cannot be empty.")
                else:
                    # Save updates to Supabase
                    if update_reminder(rem_id, edit_med, str(edit_start), str(edit_end)):
                        st.success("✅ Medication updated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to update medication.")
        with btn_c2:
            if st.button("🗑️ Delete Medication", use_container_width=True):
                # Remove from Supabase
                if delete_reminder(rem_id):
                    st.success("✅ Medication deleted successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to delete medication.")

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