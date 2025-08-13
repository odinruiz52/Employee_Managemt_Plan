# Employee Management System (Django)

A Django-based Employee Management System with API endpoints, database seeding, authentication, and optional data visualizations.

---

## 🚀 Features
- **Employee, Department, Attendance, and Performance Models**
- **PostgreSQL Database** with `.env` configuration
- **Database Seeding** using Faker
- **CRUD APIs** with Django REST Framework
- **Filtering, Pagination, and Sorting**
- **Authentication** using DRF SimpleJWT
- **Swagger UI** for API documentation
- **(Optional)** Chart.js visualizations

---

## 📦 Tech Stack
- **Backend:** Django 4.x, Django REST Framework
- **Database:** PostgreSQL
- **Auth:** DRF SimpleJWT
- **Docs:** drf-yasg (Swagger)
- **Data Seeding:** Faker
- **Optional Visualization:** Chart.js

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/employee-management.git
cd employee-management
```

### 2️⃣ Create and Activate Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables
- Create a `.env` file in the root folder based on `.env.example`:
```env
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=postgres://username:password@localhost:5432/dbname
```

### 5️⃣ Run Migrations
```bash
python manage.py migrate
```

### 6️⃣ Seed Database with Fake Data
```bash
python manage.py seed_data
```

### 7️⃣ Run Development Server
```bash
python manage.py runserver
```
- Access at: `http://127.0.0.1:8000`

---

## 🔑 Authentication
- Obtain JWT token:
```http
POST /api/auth/token/
```
- Include in request headers:
```
Authorization: Bearer <your_access_token>
```

---

## 📜 API Documentation
Swagger UI is available at:
```
http://127.0.0.1:8000/swagger/
```
Redoc UI:
```
http://127.0.0.1:8000/redoc/
```

### 📋 Common API Examples

#### 1. Authentication
```bash
# Get JWT Token
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 2. Employee Management
```bash
# List all employees (with pagination)
curl -X GET http://127.0.0.1:8000/api/v1/employees/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Create new employee
curl -X POST http://127.0.0.1:8000/api/v1/employees/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@company.com",
    "department": 1,
    "salary": "75000.00",
    "hire_date": "2024-01-15"
  }'

# Get employee by ID
curl -X GET http://127.0.0.1:8000/api/v1/employees/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Update employee
curl -X PATCH http://127.0.0.1:8000/api/v1/employees/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"salary": "80000.00"}'
```

#### 3. Department Management
```bash
# List departments
curl -X GET http://127.0.0.1:8000/api/v1/departments/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Create department
curl -X POST http://127.0.0.1:8000/api/v1/departments/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Engineering", "description": "Software development team"}'
```

#### 4. Attendance Tracking
```bash
# Record attendance
curl -X POST http://127.0.0.1:8000/api/v1/attendance/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee": 1,
    "date": "2024-01-15",
    "status": "Present",
    "notes": "On time"
  }'

# Get attendance records with filtering
curl -X GET "http://127.0.0.1:8000/api/v1/attendance/?employee=1&date_after=2024-01-01" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 5. Performance Reviews
```bash
# Create performance review
curl -X POST http://127.0.0.1:8000/api/v1/performance/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee": 1,
    "rating": 4,
    "review_date": "2024-01-15",
    "comments": "Excellent performance this quarter"
  }'
```

#### 6. Health Monitoring
```bash
# Check system health
curl -X GET http://127.0.0.1:8000/api/health/

# Detailed health check
curl -X GET http://127.0.0.1:8000/api/health/detailed/

# Async health check
curl -X GET http://127.0.0.1:8000/api/health/async/
```

### 🔍 API Features
- **Pagination**: All list endpoints support `?page=1&page_size=20`
- **Filtering**: Use query parameters like `?department=1&is_active=true`
- **Ordering**: Sort results with `?ordering=-created_at` or `?ordering=name`
- **Search**: Search employees with `?search=john`
- **API Versioning**: Use `/api/v1/` or `/api/v2/` in URLs

---

## 📊 Optional Visualizations
If enabled:
- **Employees per Department** (Pie Chart)
- **Monthly Attendance Overview** (Bar Chart)
- Accessible via `/charts/`

---

## 🛠 Management Commands
- `python manage.py seed_data` → Seeds the database with 30–50 employees and related records.

---

## 📂 Project Structure
```
employee_management/
├── employees/                # Employee app
├── attendance/               # Attendance app
├── performance/              # Performance app
├── employee_management/      # Project settings
├── templates/
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Deployment Guide

### Production Deployment Checklist

#### 1️⃣ Environment Setup
```bash
# Set production environment variables
DEBUG=False
SECRET_KEY=your-super-secure-production-key
DATABASE_URL=postgres://user:pass@localhost:5432/prod_db
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

#### 2️⃣ Security Configuration
- ✅ Generate strong `SECRET_KEY` using `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- ✅ Configure SSL/HTTPS for production domains
- ✅ Update `ALLOWED_HOSTS` with your domain names
- ✅ Set up firewall rules for database access

#### 3️⃣ Database Setup
```bash
# Create production database
createdb employee_management_prod

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

#### 4️⃣ Web Server Configuration (Nginx + Gunicorn)
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn employee_project.wsgi:application --bind 0.0.0.0:8000

# Sample Nginx configuration
server {
    listen 80;
    server_name yourdomain.com;
    
    location /static/ {
        alias /path/to/your/staticfiles/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 5️⃣ Process Management (Systemd)
```ini
# /etc/systemd/system/employee-management.service
[Unit]
Description=Employee Management Django App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/venv/bin/gunicorn --workers 3 --bind unix:/path/to/your/project/employee_management.sock employee_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### 6️⃣ Monitoring & Logging
- Monitor health endpoints: `/api/health/`, `/api/health/detailed/`
- Check log files in `logs/django.log`
- Set up alerts for system failures
- Monitor database performance and disk usage

#### 7️⃣ Backup Strategy
```bash
# Database backup
pg_dump employee_management_prod > backup_$(date +%Y%m%d).sql

# Automated backup script (crontab)
0 2 * * * /usr/bin/pg_dump employee_management_prod > /backups/daily_$(date +\%Y\%m\%d).sql
```

### 🔧 Development vs Production Differences
| Feature | Development | Production |
|---------|-------------|------------|
| DEBUG | True | False |
| Database | SQLite/Local PostgreSQL | Production PostgreSQL |
| Secret Key | Simple | Cryptographically secure |
| HTTPS | Optional | Required |
| Logging | Console | File + External service |
| Caching | Local memory | Redis/Memcached |

---

## 📄 License
This project is for internship/demo purposes only.
