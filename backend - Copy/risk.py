# ---------------- RISK CALCULATION ----------------

def calculate_risk(bp, sugar, hr):
    """
    Calculates the health risk level based on:
    - Blood Pressure
    - Sugar Level
    - Heart Rate
    """

    # High Risk
    if bp > 160 or sugar > 250 or hr > 120:
        return "High Risk"

    # Warning
    elif bp > 140 or sugar > 180 or hr > 100:
        return "Warning"

    # Normal
    else:
        return "Normal"


# ---------------- HEALTH STATUS ----------------

def get_health_status(bp, sugar, hr):
    """
    Returns a detailed health status message.
    """

    risk = calculate_risk(bp, sugar, hr)

    if risk == "High Risk":
        return (
            "⚠️ High Risk\n"
            "Please contact your caregiver or visit the nearest hospital immediately."
        )

    elif risk == "Warning":
        return (
            "⚠️ Warning\n"
            "Your health readings are above the normal range. Monitor your condition carefully."
        )

    return (
        "✅ Normal\n"
        "Your health readings are within the normal range. Keep maintaining a healthy lifestyle."
    )