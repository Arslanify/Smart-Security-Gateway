# 🛡️ University Smart Gateway System

An AI-powered university access control and attendance management system with face recognition, QR verification, fingerprint support, and live bus tracking.

## ✨ Features

- **Face Recognition** — DeepFace (Facenet512) powered identity verification
- **QR Code Verification** — Signed, tamper-proof QR codes for each entity
- **Fingerprint Support** — Biometric ID-based verification
- **Attendance Tracking** — Smart entry/exit logging with cooldown timer
- **WhatsApp Alerts** — Real-time guardian notifications via Twilio
- **Live Bus Tracking** — GPS-based bus tracking with Leaflet maps
- **Admin Dashboard** — Live analytics with Chart.js visualizations
- **Multi-Role Support** — Students, Faculty, Staff, Guards, Visitors, Vehicles

## 🗂️ Project Structure

```
university_auth/
├── core/               # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── verifier/           # Main app
│   ├── models.py       # Entity, AttendanceLog, BusLocation
│   ├── views.py        # All API & page views
│   ├── urls.py         # URL routing
│   ├── admin.py        # Admin panel config
│   ├── utils.py        # DeepFace AI utilities
│   └── templates/      # HTML templates
│       ├── index.html
│       ├── admin_panel.html
│       ├── attendance_report.html
│       └── tracking.html
├── requirements.txt
├── .env.example        # Copy this to .env
└── manage.py
```

## 🚀 Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/university-smart-gateway.git
cd university-smart-gateway
```

### 2. Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup environment variables
```bash
cp .env.example .env
# .env file mein apni values fill karein
```

### 5. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Start the server
```bash
python manage.py runserver
```

## ⚙️ Configuration

`.env` file mein yeh values set karein:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `MASTER_ADMIN_USER` | Admin login username |
| `MASTER_ADMIN_PASS` | Admin login password |
| `EMAIL_HOST_USER` | Gmail address for alerts |
| `EMAIL_HOST_PASSWORD` | Gmail App Password |

## 🔗 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/register/` | POST | Register new entity |
| `/verify/` | POST | Face verification |
| `/verify-qr/` | POST | QR code verification |
| `/verify-fingerprint/` | POST | Fingerprint verification |
| `/login/` | POST | Staff/Admin login |
| `/admin-panel/` | GET | Admin dashboard |
| `/api/update-location/` | POST | Update bus GPS |
| `/api/get-location/` | GET | Get bus location |
| `/swagger/` | GET | API documentation |

## 🛠️ Tech Stack

- **Backend:** Django, Django REST Framework
- **AI:** DeepFace (Facenet512), OpenCV
- **Frontend:** HTML, CSS, Chart.js, Leaflet.js
- **Notifications:** Twilio WhatsApp API
- **Database:** SQLite (dev) / PostgreSQL (prod)
