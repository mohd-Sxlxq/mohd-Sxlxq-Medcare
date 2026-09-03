import pandas as pd
from datetime import datetime, timedelta
from typing import cast, Any, List, Dict
from backend.supabase_client import supabase

def create_reminder_table():
    print("✅ Reminder table is managed by Supabase.")

def save_reminder(
    medicine: str,
    start_time: str,
    end_time: str,
    senior: str,
    duration_days: int = 1
):
    try:
        senior_clean = senior.strip().lower()
        medicine_clean = medicine.strip()
        base_date = datetime.now().date()
        
        # Cap duration between 1 and 90 days
        duration_days = max(1, min(int(duration_days), 90))

        records_to_insert = []
        for i in range(duration_days):
            target_date = base_date + timedelta(days=i)
            records_to_insert.append({
                "senior": senior_clean,
                "medicine": medicine_clean,
                "start_time": start_time,
                "end_time": end_time,
                "reminder_date": target_date.strftime("%Y-%m-%d"),
                "taken": "No",
                "notified": "No"
            })

        response = (
            supabase
            .table("reminders")
            .insert(records_to_insert)
            .execute()
        )

        return bool(response.data)

    except Exception as e:
        print("❌ Save reminder error:", e)
        return False

def get_reminders_for_senior(senior: str):
    try:
        today_str = datetime.now().strftime("%Y-%m-%d")
        response = (
            supabase
            .table("reminders")
            .select("id,medicine,start_time,end_time,taken,notified,reminder_date")
            .eq("senior", senior.strip().lower())
            .eq("reminder_date", today_str)
            .order("start_time")
            .execute()
        )

        rows = cast(List[Dict[str, Any]], response.data)
        records = []

        for row in rows:
            records.append({
                "id": row.get("id"),
                "Medicine": row.get("medicine"),
                "Start": row.get("start_time"),
                "End": row.get("end_time"),
                "Taken": row.get("taken"),
                "Notified": row.get("notified"),
                "Date": row.get("reminder_date")
            })

        return pd.DataFrame(records)

    except Exception as e:
        print("❌ Get reminders error:", e)
        return pd.DataFrame()

def mark_taken(reminder_id: int):
    try:
        response = (
            supabase
            .table("reminders")
            .update({"taken": "Yes"})
            .eq("id", reminder_id)
            .execute()
        )
        return bool(response.data)
    except Exception as e:
        print("❌ Mark taken error:", e)
        return False

def mark_notified(reminder_id: int):
    try:
        response = (
            supabase
            .table("reminders")
            .update({"notified": "Yes"})
            .eq("id", reminder_id)
            .execute()
        )
        return bool(response.data)
    except Exception as e:
        print("❌ Mark notified error:", e)
        return False