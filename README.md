# Shri Ji Classes — Backend Setup Guide

## What You Need First
- Python 3.10+  →  https://python.org/downloads
- PostgreSQL 15+ →  https://postgresql.org/download (Windows installer)
- Node.js 18+   →  https://nodejs.org (for the frontend)

---

## STEP 1 — Set Up PostgreSQL

After installing PostgreSQL, open **pgAdmin** or the SQL Shell and run:

```sql
CREATE DATABASE shriji_classes;
```

That's it. Remember your PostgreSQL password (set during installation).

---

## STEP 2 — Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and fill in:

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/shriji_classes
SECRET_KEY=any_long_random_string_like_abc123xyz789
FAST2SMS_API_KEY=your_key_here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin@shriji123
FRONTEND_URL=http://localhost:3000
```

---

## STEP 3 — Get Your Fast2SMS API Key (FREE)

1. Go to **https://www.fast2sms.com**
2. Sign up with your mobile number (Indian number required)
3. Verify email → Login
4. Go to **Dashboard → Dev API**
5. Copy the **API Key**
6. Paste it in `.env` as `FAST2SMS_API_KEY`

> **Free plan gives ₹50 credits** — enough for ~200 OTPs to test.
> Recharge when needed (very cheap, ~₹0.20 per SMS).

---

## STEP 4 — Install Python Dependencies

```bash
cd shriji-backend
pip install -r requirements.txt
```

---

## STEP 5 — Start the Backend

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
✅ Default admin created
🚀 Shri Ji Classes API started
📖 API docs: http://localhost:8000/docs
```

Open **http://localhost:8000/docs** in browser — you'll see all API endpoints!

---

## STEP 6 — Connect the Frontend

In your React frontend (`shriji-classes` folder), create a `.env` file:

```
REACT_APP_API_URL=http://localhost:8000
```

Then update `src/context/AppContext.js` to use API calls instead of seed data.
(See `API_INTEGRATION.md` for the complete updated AppContext with real API calls.)

---

## STEP 7 — Start the Frontend

```bash
cd shriji-classes
npm start
```

Open **http://localhost:3000**

---

## Login Credentials

| Role   | Field     | Value               |
|--------|-----------|---------------------|
| Admin  | Username  | admin               |
| Admin  | Password  | admin@shriji123     |
| Parent | Phone     | (registered phone)  |
| Parent | OTP       | Sent via Fast2SMS   |

---

## API Endpoints Summary

| Method | Endpoint                      | Who        | Purpose                  |
|--------|-------------------------------|------------|--------------------------|
| POST   | /auth/admin/login             | Admin      | Login with password      |
| POST   | /auth/parent/send-otp         | Parent     | Request OTP via SMS      |
| POST   | /auth/parent/verify-otp       | Parent     | Verify OTP, get token    |
| GET    | /students/                    | Admin      | List all students        |
| POST   | /students/                    | Admin      | Add new student          |
| PUT    | /students/{id}                | Admin      | Update student           |
| DELETE | /students/{id}                | Admin      | Delete (soft) student    |
| GET    | /fees/                        | Both       | List fee records         |
| POST   | /fees/                        | Admin      | Create fee record        |
| PATCH  | /fees/{id}/mark-paid          | Admin      | Mark fee as paid         |
| GET    | /marks/                       | Both       | List marks               |
| POST   | /marks/                       | Admin      | Add marks                |
| PUT    | /marks/{id}                   | Admin      | Update marks             |
| DELETE | /marks/{id}                   | Admin      | Delete marks             |
| GET    | /attendance/                  | Both       | List attendance          |
| POST   | /attendance/upsert            | Admin      | Mark/update attendance   |
| GET    | /notes/                       | Both       | List study materials     |
| POST   | /notes/                       | Admin      | Upload PDF/file          |
| GET    | /notes/{id}/download          | Both       | Download file            |
| DELETE | /notes/{id}                   | Admin      | Delete note              |

---

## Folder Structure

```
shriji-backend/
├── main.py                  ← Entry point, starts server
├── requirements.txt         ← Python packages
├── .env                     ← Your config (never share this!)
├── .env.example             ← Template
├── uploads/                 ← Uploaded PDF notes stored here
└── app/
    ├── database.py          ← PostgreSQL connection
    ├── models.py            ← Database tables (SQLAlchemy)
    ├── schemas.py           ← Request/response validation
    ├── routers/
    │   ├── auth.py          ← Login, OTP routes
    │   ├── students.py      ← Student CRUD
    │   ├── fees.py          ← Fee management
    │   └── academics.py     ← Marks, Attendance, Notes
    ├── services/
    │   └── otp_service.py   ← Fast2SMS integration
    └── utils/
        ├── security.py      ← JWT, password hashing
        └── deps.py          ← Auth middleware
```

---

## Troubleshooting

**"Connection refused" on PostgreSQL**
→ Make sure PostgreSQL service is running. Open Services → PostgreSQL → Start

**"Module not found"**
→ Run `pip install -r requirements.txt` again

**OTP not arriving**
→ Check your Fast2SMS balance at fast2sms.com dashboard
→ In dev mode (no API key), OTP prints to the terminal window

**CORS error in browser**
→ Make sure FRONTEND_URL in .env matches exactly where React is running
