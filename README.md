# Finance Dashboard Backend API

This repository contains the backend architecture for the Finance Dashboard. It is built strictly using **Django** and **Django REST Framework (DRF)**.

The framework was designed around a **Decoupled Architecture**, keeping the APIs strictly separated from the frontend to allow for independent scaling, testing, and future integrations (such as mobile apps).

---

## 🏗️ Architecture & App Structure

The backend relies on the **Single Responsibility Principle**. Instead of throwing all views and models into one file, the system is split into three core isolated apps:

1. **`users` (Access Control & Identity)**
   - Manages JWT Authentication using `djangorestframework-simplejwt`.
   - Uses Django Signals to map a native `User` to a custom `UserProfile` (One-to-One).
   - Enforces the Three-Tier Role System required by the spec: _Viewer_, _Analyst_, and _Admin_.
   
2. **`finance` (Data Management)**
   - Manages the core `FinanceRecord` model (amount, category, type, description, date).
   - Features an ultra-simplified and clean bulk CSV/Excel (`.xlsx`) upload processor. By skipping noisy legacy looping, it uses `.to_dict('records')` unpacking (`**row`) to intelligently and cleanly migrate Pandas dataframes perfectly to the SQLite DB simultaneously.
   
3. **`dashboard` (Analytics)**
   - A pure aggregate API layer processing multi-metric payloads. 
   - Dynamically analyzes "Total Expenses", "Income", "Net Balance", and **"Today's Expenses"** in real-time leveraging Django's SQL `aggregate(Sum())`.
   - Also maps 12 full trailing fiscal months for seamless frontend layout plotting.

---

## 🔐 Access Control Logic (Permissions)

Access control operates completely at the middleware/decorator level. We implemented custom BasePermissions in `users/permissions.py`:

- **Admin**: Has full CRUD overhead. Can reach the `/users/management/` endpoints.
- **Analyst**: Has read-only access to global financial data pipelines for analysis but is blocked from mutating records.
- **Viewer**: Strictly limited to viewing aggregated `/dashboard/` charts. Blocked completely from viewing raw financial line items.

---

## ⚙️ Running Locally

### 1. Prerequisites
- Python 3.10+
- Pandas & Openpyxl (For advanced data operations)

### 2. Setup
Navigate into the backend folder, create a virtual environment, and install dependencies:
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

*(Note: If you do not have a requirements.txt, ensure `django`, `djangorestframework`, `djangorestframework-simplejwt`, `django-cors-headers`, `pandas`, `openpyxl`, and `django-filter` are installed).*

### 3. Database Migration
This project relies on SQLite3 out of the box for assignment simplicity and portability. Setup the schema:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Run the Server
```bash
python manage.py runserver
```

---

## 🛠️ API Reference

### Auth & Users
- `POST /api/users/login/` - Returns JWT Access & Refresh Tokens
- `POST /api/users/register/` - Creates new Viewer account
- `GET/POST /api/users/management/` - Admin route for toggling user roles/status

### Finance Data
- `GET /api/finance/records/` - Retrieve all transactions (Filters: `?type=income&category=Salary`)
- `POST /api/finance/records/` - **New:** Standard endpoint for parsing singular manual data transactions quickly.
- `POST /api/finance/records/upload_csv/` - `multipart/form-data` bulk upload endpoint (via Unpacking loops). Expects headers: `date, title, category, amount, type`.
- `GET /api/finance/records/export_csv/` - Streams filtered dataset back as downloadable blob.

### Dashboard
- `GET /api/dashboard/metrics/summary/` - Returns high-level sum items (Total Income, Total Expenses, **Today's Expenses**, Categories).
- `GET /api/dashboard/metrics/metrics/` - Aggregated full 12-month trend pipeline specifically targeting Recharts mapping.
