import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

from backend.user import (
    get_connected_caregivers,
    get_user_email
)

load_dotenv()

SENDER = os.getenv("EMAIL_SENDER", "")
PASSWORD = os.getenv("EMAIL_PASSWORD", "")

print("Sender:", SENDER)
print("Password Length:", len(PASSWORD))


# ---------------- SEND EMAIL ----------------

def send_email(receiver, subject, body):

    if not SENDER or not PASSWORD:
        print("Email sender credentials not configured.")
        return

    if not receiver:
        print("No receiver email.")
        return

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = SENDER
    msg["To"] = receiver

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        server.login(
            SENDER,
            PASSWORD
        )

        server.send_message(msg)
        server.quit()

        print(f"✅ Email sent to {receiver}")

    except Exception as e:
        print("Email Error:", e)


# ---------------- HIGH RISK ALERT ----------------

def send_email_alert(
    senior,
    bp,
    sugar,
    hr,
    risk
):

    caregivers = get_connected_caregivers(senior)

    if not caregivers:
        print("No caregivers connected.")
        return

    subject = "🚨 MedCare High Health Risk Alert"

    body = f"""
Dear Caregiver,

A high health risk has been detected.

Senior : {senior}

Blood Pressure : {bp}
Sugar Level    : {sugar}
Heart Rate     : {hr}

Risk Level : {risk}

Please check on the senior immediately.

Regards,
MedCare Emergency Monitoring System
"""

    for caregiver in caregivers:

        receiver =caregiver[2]

        if receiver:
            send_email(
                receiver,
                subject,
                body
            )


# ---------------- MISSED MEDICATION ALERT ----------------

def send_missed_med_alert(
    senior,
    medicine
):

    caregivers = get_connected_caregivers(senior)

    if not caregivers:
        print("No caregivers connected.")
        return

    subject = "⚠ MedCare Medication Reminder Missed"

    body = f"""
Dear Caregiver,

The following medication was not taken.

Senior : {senior}

Medicine : {medicine}

Please contact the senior.

Regards,
MedCare Emergency Monitoring System
"""

    for caregiver in caregivers:

        receiver =caregiver[2]

        if receiver:
            send_email(
                receiver,
                subject,
                body
            )