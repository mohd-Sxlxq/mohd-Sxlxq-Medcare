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
# SAVE REMINDER (CREATE)
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
# GET REMINDERS FOR SENIOR (READ)
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
            
            # This proves to the code editor that 'row' is a dictionary
            # and automatically removes the red underlines on .get()
            if isinstance(row, dict):
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


# =========================================================
# UPDATE REMINDER (UPDATE)
# =========================================================

def update_reminder(reminder_id, medicine, start_time, end_time):

    try:

        response = (
            supabase
            .table("reminders")
            .update({
                "medicine": medicine.strip(),
                "start_time": start_time,
                "end_time": end_time
            })
            .eq("id", reminder_id)
            .execute()
        )

        return True

    except Exception as e:

        print("❌ Update reminder error:", e)
        return False


# =========================================================
# DELETE REMINDER (DELETE)
# =========================================================

def delete_reminder(reminder_id):

    try:

        response = (
            supabase
            .table("reminders")
            .delete()
            .eq("id", reminder_id)
            .execute()
        )

        return True

    except Exception as e:

        print("❌ Delete reminder error:", e)
        return False