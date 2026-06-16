# Smart Dustbin Management System — Backend

## Quick Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup PostgreSQL
```bash
# Create database
createdb smart_dustbin
```

### 3. Configure .env
Edit `.env` and fill in your:
- DATABASE_URL
- SECRET_KEY (any random string)
- Twilio credentials (for SMS)
- SMTP credentials (for email)

### 4. Run the server
```bash
uvicorn main:app --reload
```

### 5. API Docs
Open browser: http://localhost:8000/docs

---

## Create First Admin Account
POST http://localhost:8000/auth/register
```json
{
  "full_name": "Admin User",
  "email": "admin@example.com",
  "password": "yourpassword",
  "role": "admin"
}
```

## ESP8266 Sensor Data Endpoint
POST http://localhost:8000/dustbins/sensor-data
```json
{
  "bin_code": "BIN-001",
  "distance_cm": 35.5
}
```

---

## Folder Structure
```
smart_dustbin_backend/
├── main.py               # Entry point
├── .env                  # Configuration
├── requirements.txt      # Dependencies
├── core/                 # Config, DB, Security
├── models/               # Database tables
├── schemas/              # Request/Response shapes
├── routers/              # API endpoints
├── services/             # MQTT, Alerts, Scheduler
└── middleware/           # Role-based access control
```

## Roles
| Role       | Access Level          |
|------------|-----------------------|
| admin      | Full access           |
| supervisor | Area-level access     |
| collector  | Own tasks only        |
