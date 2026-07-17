# MedCare - Smart Healthcare Assistance System

## 📌 Project Overview

**MedCare** is a smart healthcare assistance platform designed to help senior citizens manage their daily healthcare activities while keeping caregivers connected and informed.

The system focuses on medication reminders, health monitoring, caregiver connection, emergency assistance, and multilingual support to improve the safety and independence of elderly users.

---

# 🎯 Objectives

* Help senior citizens remember their medications on time.
* Allow caregivers to monitor seniors remotely.
* Provide emergency assistance during critical situations.
* Reduce dependency on manual healthcare tracking.
* Provide an easy-to-use interface for elderly users.

---

# 🚀 Main Features

## 👴 Senior Citizen Module

### Registration

Senior users can create an account with:

* Full Name
* Email Address
* Mobile Number
* Permanent Address
* Password

### Medication Management

* Add medicines
* Set medication schedules
* Receive reminders
* Track missed medications

### Health Monitoring

* Store health information
* Analyze health conditions
* Generate risk alerts

### Emergency Support

* SOS emergency feature
* Share location during emergency (Android app)
* Send emergency details to caregiver

---

# 👨‍👩‍👧 Caregiver Module

Caregivers can:

* Create their own account
* Connect with seniors using a secure connection code
* Receive alerts
* Monitor medication status
* View health updates

---

# 🔐 Senior-Caregiver Connection System

MedCare uses a secure connection code system.

Workflow:

1. Senior receives a permanent connection code.
2. Senior shares the code with the caregiver.
3. Caregiver enters the code to connect.
4. Both accounts become linked.

Benefits:

* No admin approval required.
* Supports multiple users.
* Maintains user privacy.
* Same code can be reused for web access.

---

# 📧 Notification System

MedCare supports:

## Email Notifications

Using SMTP:

* Missed medication alerts
* Health risk alerts
* Emergency notifications

## Future Mobile Notifications

Android app support will include:

* Push notifications
* SMS support
* Emergency alerts

---

# 🌐 Language Support

MedCare supports:

* English
* Kannada (ಕನ್ನಡ)

The system is designed for easy addition of more languages in the future.

---

# 📍 Location System

## Website

Stores:

* Permanent address
* Emergency contact information

## Android Application

Provides:

* Live GPS location
* Emergency location sharing
* Ambulance assistance support

---

# 🚑 Emergency Assistance (Future)

Planned integration with an AI receptionist system.

Emergency flow:

```
Missed medication detection

        ↓

Caregiver notification

        ↓

Emergency confirmation

        ↓

AI receptionist connection

        ↓

Ambulance assistance
```

---

# 🛠️ Technology Stack

## Frontend

* Streamlit
* HTML/CSS
* Bootstrap

## Backend

* FastAPI

## Database

* SQLite

## Authentication

* Secure login system
* Role-based access

## Notifications

* SMTP Email Service
* Future SMS Gateway
* Mobile Push Notifications

---

# 📂 Project Structure

```
MedCare/

│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── auth.py
│   ├── medication.py
│   ├── notification.py
│   └── email_service.py
│
├── frontend/
│   ├── login.py
│   ├── signup.py
│   ├── senior_dashboard.py
│   └── caregiver_dashboard.py
│
├── database/
│   └── medcare.db
│
├── requirements.txt
│
└── README.md
```

---

# 🔮 Future Enhancements

* Android application
* SMS alerts
* AI health prediction
* Hospital integration
* Mono language support

---

# 👨‍💻 Project Purpose

MedCare aims to provide a simple, secure, and accessible healthcare companion for senior citizens by combining technology with caregiver support.

---

# 📄 License

This project is developed for educational and research purposes.
