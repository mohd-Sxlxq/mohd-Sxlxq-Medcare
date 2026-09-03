import pandas as pd
from datetime import datetime
from typing import cast, Any, List, Dict

from backend.supabase_client import supabase


# =========================================================
# CREATE HEALTH TABLE
# =========================================================
# Table creation is handled in Supabase SQL Editor.
# This function is kept for compatibility with the old code.

def create_health_table():
    print("✅ Health table is managed by Supabase.")


# =========================================================
# SAVE HEALTH RECORD
# =========================================================

def save_health_record(senior: str, bp: str, sugar: str, hr: str, risk: str):

    try:

        now = datetime.now()

        data = {
            "senior": senior.strip().lower(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "blood_pressure": bp,
            "sugar_level": sugar,
            "heart_rate": hr,
            "risk_level": risk
        }

        response = (
            supabase
            .table("health")
            .insert(data)
            .execute()
        )

        return bool(response.data)

    except Exception as e:

        print("❌ Save health record error:", e)
        return False


# =========================================================
# GET LATEST HEALTH
# =========================================================

def get_latest_health(senior: str):

    try:

        response = (
            supabase
            .table("health")
            .select(
                "blood_pressure,sugar_level,heart_rate"
            )
            .eq("senior", senior.strip().lower())
            .order("id", desc=True)
            .limit(1)
            .execute()
        )

        data = cast(List[Dict[str, Any]], response.data)

        if data:

            row = data[0]

            return (
                row["blood_pressure"],
                row["sugar_level"],
                row["heart_rate"]
            )

        return None, None, None

    except Exception as e:

        print("❌ Get latest health error:", e)
        return None, None, None


# =========================================================
# LAST 7 RECORDS
# =========================================================

def get_last_7_records(senior: str):

    try:

        response = (
            supabase
            .table("health")
            .select(
                "date,time,blood_pressure,"
                "sugar_level,heart_rate,risk_level"
            )
            .eq("senior", senior.strip().lower())
            .order("id", desc=True)
            .limit(7)
            .execute()
        )

        rows = cast(List[Dict[str, Any]], response.data)

        records = []

        for row in rows:

            records.append({
                "Date": row.get("date"),
                "Time": row.get("time"),
                "Blood Pressure": row.get("blood_pressure"),
                "Sugar Level": row.get("sugar_level"),
                "Heart Rate": row.get("heart_rate"),
                "Risk Level": row.get("risk_level")
            })

        return pd.DataFrame(records)

    except Exception as e:

        print("❌ Get last 7 records error:", e)
        return pd.DataFrame()


# =========================================================
# FULL HISTORY
# =========================================================

def get_all_records(senior: str):

    try:

        response = (
            supabase
            .table("health")
            .select(
                "date,time,blood_pressure,"
                "sugar_level,heart_rate,risk_level"
            )
            .eq("senior", senior.strip().lower())
            .order("id", desc=True)
            .execute()
        )

        rows = cast(List[Dict[str, Any]], response.data)

        records = []

        for row in rows:

            records.append({
                "Date": row.get("date"),
                "Time": row.get("time"),
                "Blood Pressure": row.get("blood_pressure"),
                "Sugar Level": row.get("sugar_level"),
                "Heart Rate": row.get("heart_rate"),
                "Risk Level": row.get("risk_level")
            })

        return pd.DataFrame(records)

    except Exception as e:

        print("❌ Get all records error:", e)
        return pd.DataFrame()


# =========================================================
# GET LATEST RISK
# =========================================================

def get_latest_risk(senior: str):

    try:

        response = (
            supabase
            .table("health")
            .select("risk_level")
            .eq("senior", senior.strip().lower())
            .order("id", desc=True)
            .limit(1)
            .execute()
        )

        data = cast(List[Dict[str, Any]], response.data)

        if data:

            return data[0].get("risk_level")

        return None

    except Exception as e:

        print("❌ Get latest risk error:", e)
        return None