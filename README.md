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

## 📄 License
This project is for internship/demo purposes only.
