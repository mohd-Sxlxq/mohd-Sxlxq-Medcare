import streamlit as st
import matplotlib.pyplot as plt

from backend.user import get_my_seniors
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

    # ================= CONNECTED SENIORS =================

    seniors = get_my_seniors(caretaker)

    st.subheader("👥 Connected Seniors")

    if not seniors:
        st.info(
            "No seniors connected.\n\n"
            "Connect a senior while creating your caregiver account."
        )
        return

    for senior in seniors:

        bp, sugar, hr = get_latest_health(senior)
        risk = get_latest_risk(senior)

        st.markdown(f"### 🧓 {senior}")

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

    # ================= ADD REMINDER =================

    st.subheader("💊 Add Medication Reminder")

    selected_senior = st.selectbox(
        "Select Senior",
        seniors,
        key="selected_senior"
    )

    medicine = st.text_input(
        "Medicine Name",
        key="medicine"
    )

    col1, col2 = st.columns(2)

    with col1:
        start_time = st.time_input(
            "Start Time",
            key="start_time"
        )

    with col2:
        end_time = st.time_input(
            "End Time",
            key="end_time"
        )

    if st.button(
        "Add Reminder",
        key="add_reminder"
    ):

        if medicine.strip() == "":
            st.warning("Enter medicine name.")

        else:

            save_reminder(
                medicine,
                str(start_time),
                str(end_time),
                selected_senior
            )

            st.success("Reminder Added Successfully")

    st.divider()

    # ================= HEALTH TRENDS =================

    st.subheader("📈 Health Trends")

    selected = st.selectbox(
        "Choose Senior",
        seniors,
        key="trend_senior"
    )

    records = get_last_7_records(selected)

    if records.empty:
        st.info("No health records found.")
        return

    records = records.iloc[::-1].reset_index(drop=True)

    records["Label"] = (
        records["Date"] +
        "\n" +
        records["Time"]
    )

    # ---------------- Blood Pressure ----------------

    st.write("### ❤️ Blood Pressure")

    fig = plt.figure(figsize=(8, 4))

    plt.plot(
        records["Label"],
        records["Blood Pressure"],
        marker="o"
    )

    plt.xticks(rotation=45)
    plt.grid(True)

    plt.tight_layout()

    st.pyplot(fig)

    # ---------------- Sugar ----------------

    st.write("### 🍬 Sugar Level")

    fig = plt.figure(figsize=(8, 4))

    plt.plot(
        records["Label"],
        records["Sugar Level"],
        marker="o"
    )

    plt.xticks(rotation=45)
    plt.grid(True)

    plt.tight_layout()

    st.pyplot(fig)

    # ---------------- Heart Rate ----------------

    st.write("### 💓 Heart Rate")

    fig = plt.figure(figsize=(8, 4))

    plt.plot(
        records["Label"],
        records["Heart Rate"],
        marker="o"
    )

    plt.xticks(rotation=45)
    plt.grid(True)

    plt.tight_layout()

    st.pyplot(fig)

    # ---------------- Risk History ----------------

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