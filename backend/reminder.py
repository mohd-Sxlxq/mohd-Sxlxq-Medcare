import pandas as pd

from backend.supabase_client import supabase


# =========================================================
# CREATE REMINDER TABLE
# =========================================================
# The actual table is created in Supabase SQL Editor.
# This function is kept so existing application code
# calling create_reminder_table() does not break.


def create_reminder_table():

    print("✅ Reminder table is managed by Supabase.")


# =========================================================
# SAVE REMINDER
# =========================================================

def save_reminder(
    medicine,
    start_time,
    end_time,
    senior
):

    try:

        data = {
            "senior": senior.strip().lower(),
            "medicine": medicine.strip(),
            "start_time": start_time,
            "end_time": end_time,
            "taken": "No",
            "notified": "No"
        }

        response = (
            supabase
            .table("reminders")
            .insert(data)
            .execute()
        )

        return bool(response.data)

    except Exception as e:

        print("❌ Save reminder error:", e)
        return False


# =========================================================
# GET REMINDERS FOR SENIOR
# =========================================================

def get_reminders_for_senior(senior):

    try:

        response = (
            supabase
            .table("reminders")
            .select(
                "id,medicine,start_time,end_time,taken,notified"
            )
            .eq(
                "senior",
                senior.strip().lower()
            )
            .order("start_time")
            .execute()
        )

        rows = response.data

        records = []

        for row in rows:

            records.append({
                "id": row.get("id"),
                "Medicine": row.get("medicine"),
                "Start": row.get("start_time"),
                "End": row.get("end_time"),
                "Taken": row.get("taken"),
                "Notified": row.get("notified")
            })

        return pd.DataFrame(records)

    except Exception as e:

        print("❌ Get reminders error:", e)
        return pd.DataFrame()


# =========================================================
# MARK AS TAKEN
# =========================================================

def mark_taken(reminder_id):

    try:

        response = (
            supabase
            .table("reminders")
            .update({
                "taken": "Yes"
            })
            .eq("id", reminder_id)
            .execute()
        )

        return bool(response.data)

    except Exception as e:

        print("❌ Mark taken error:", e)
        return False


# =========================================================
# MARK AS NOTIFIED
# =========================================================

def mark_notified(reminder_id):

    try:

        response = (
            supabase
            .table("reminders")
            .update({
                "notified": "Yes"
            })
            .eq("id", reminder_id)
            .execute()
        )

        return bool(response.data)

    except Exception as e:

        print("❌ Mark notified error:", e)
        return False