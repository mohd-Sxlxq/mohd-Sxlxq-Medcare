from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.storage import save_health_record
from backend.risk import calculate_risk
from backend.mail import send_email_alert

app = FastAPI(
    title="MedCare API",
    version="1.0"
)

# ---------------- CORS ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Change this to your website URL after deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- HOME ----------------

@app.get("/")
def home():

    return {
        "message": "MedCare API is Running"
    }


# ---------------- HEALTH SUBMISSION ----------------

@app.post("/submit-health")
def submit_health(
    senior: str,
    bp: float,
    sugar: float,
    hr: float
):

    # Calculate Risk
    risk = calculate_risk(
        bp,
        sugar,
        hr
    )

    # Save Health Record
    save_health_record(
        senior,
        bp,
        sugar,
        hr,
        risk
    )

    # Send Email if High Risk
    if risk == "High Risk":

        try:
            send_email_alert(
                senior,
                bp,
                sugar,
                hr,
                risk
            )
        except Exception as e:
            print("Email Error:", e)

    return {
        "status": "success",
        "risk_level": risk
    }


# ---------------- HEALTH CHECK ----------------

@app.get("/health")
def health():

    return {
        "status": "online"
    }