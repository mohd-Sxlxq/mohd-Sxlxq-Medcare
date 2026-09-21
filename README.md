# MedCare - Smart Healthcare Assistance System

## 📌 Project Overview

**MedCare** is a cloud-connected, smart healthcare assistance platform designed to help senior citizens manage their daily healthcare activities while keeping caregivers connected and informed.

The system focuses on medication reminders, real-time health monitoring, caregiver connection, emergency assistance, and data visualization to improve the safety and independence of elderly users.

---

# 🎯 Objectives

* Help senior citizens remember their medications on time.
* Allow caregivers to remotely monitor seniors and manage their medication schedules.
* Provide dynamic visual health trends (Blood Pressure, Sugar Level, Heart Rate).
* Reduce dependency on manual healthcare tracking.
* Provide an easy-to-use, accessible interface for elderly users.

---

# 🚀 Main Features

## 👴 Senior Citizen Module

### Registration & Connection
* Secure account creation (Full Name, Email, Mobile, Address, Password).
* Generates a unique, secure Connection Code to share with caregivers.

### Medication Management
* View daily medication schedules.
* Mark medications as "Taken" with a single click.
* Automated tracking of missed medications.

### Health Monitoring
* Input daily health metrics (Blood Pressure, Sugar Levels, Heart Rate).
* Automated risk calculation (Normal, Warning, High Risk).
* Direct saving to the cloud database.

---

# 👨‍⚕️ Caregiver Module

Caregivers can remotely manage and monitor their connected seniors:

* **Secure Connection:** Link with multiple seniors using their unique Connection Codes.
* **Medication CRUD Operations:** Create, Read, Update, and Delete medication schedules dynamically for each senior.
* **Health Trends Visualization:** View automated line charts (powered by Matplotlib & Pandas) tracking the senior's 7-day health history.
* **Instant Alerts:** Receive notifications and view high-risk health submissions in real-time.

---

# 🔐 Senior-Caregiver Connection System

MedCare uses a secure connection code system ensuring privacy and ease of use.

Workflow:
1. Senior receives a permanent connection code upon registration.
2. Senior shares the code with their caregiver.
3. Caregiver enters the code into their dashboard to connect.
4. Both accounts become securely linked in the database.

Benefits:
* No manual admin approval required.
* Supports one caregiver monitoring multiple seniors.
* Maintains strict user privacy (caregivers only see data for connected seniors).

---

# 📧 Notification System

MedCare currently supports **Automated Email Notifications** via SMTP:
* Missed medication alerts sent directly to the caregiver.
* High-risk health metric alerts (BP, Sugar, HR spikes).

*(Future updates will include Android push notifications and SMS support).*

---

# 🛠️ Technology Stack

## Frontend (User Interface)
* **Streamlit:** Core framework for the interactive web dashboards.
* **Pandas:** Data manipulation and tabular history displays.
* **Matplotlib:** Graphical visualization for health trends.

## Backend (Server & API)
* **Python:** Core backend logic.
* **FastAPI:** API routing for external system integration.

## Database & Cloud
* **Supabase (PostgreSQL):** Cloud database replacing local SQLite for real-time, secure data storage.

---

# 📂 Project Structure

```text
MedCare/
│
├── backend/
│   ├── api.py                 # FastAPI endpoints
│   ├── supabase_client.py     # Cloud database connection
│   ├── auth.py                # Authentication logic
│   ├── user.py                # User and connection management
│   ├── risk.py                # Health risk calculation logic
│   ├── storage.py             # Health record CRUD
│   ├── reminder.py            # Medication CRUD operations
│   └── mail.py                # SMTP email alert system
│
├── frontend/
│   ├── auth.py                # Login/Signup UI
│   ├── senior_dash.py         # Senior Citizen interface
│   └── caretaker_dash.py      # Caregiver interface (Charts & Management)
│
├── app.py                     # Main Streamlit application entry point
├── .env                       # Environment variables (Supabase keys, Email credentials)
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
