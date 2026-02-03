# 🧪 Chemical Equipment Parameter Visualizer

A hybrid **Web + Desktop application** for visualizing chemical equipment parameters with built-in **AI anomaly detection**.

Monitor equipment, analyze trends, and detect anomalies in real time using both browser and desktop dashboards.

---

## 🚀 Tech Stack

**Backend**
- Django
- Django REST Framework

**Web Frontend**
- React
- Chart.js

**Desktop Frontend**
- PyQt5
- Matplotlib

**AI**
- Isolation Forest (Anomaly Detection)

---

## 📁 Project Structure

```
chemical-visualizer/
│
├── backend/            # Django REST API
├── web_frontend/       # React dashboard
├── desktop_frontend/   # PyQt5 desktop application
└── README.md
```

---

## ⚙️ Setup Instructions

### Backend (Django API)

```bash
cd backend
python -m venv venv
```

Activate virtual environment:

Windows:
```bash
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Apply migrations:
```bash
python manage.py migrate
```

Create admin user:
```bash
python manage.py createsuperuser
```

Run server:
```bash
python manage.py runserver
```

Backend URL:
```
http://127.0.0.1:8000
```

---

### Web Frontend (React Dashboard)

```bash
cd web_frontend
npm install
npm start
```

Frontend URL:
```
http://localhost:3000
```

---

### Desktop Frontend (PyQt5 Application)

```bash
cd desktop_frontend
pip install -r requirements.txt
python main.py
```

---

## 🤖 AI Anomaly Detection

Uses **Isolation Forest** to automatically detect abnormal equipment behavior.

Workflow:
1. Collect sensor data
2. Train model
3. Detect anomalies
4. Highlight outliers in visualizations

Applications:
- Fault detection
- Preventive maintenance
- Safety monitoring

---

## ✨ Features

- Web + Desktop interfaces
- REST API backend
- Machine learning anomaly detection
- Modular architecture
- Easy setup

---

## 🛠️ Troubleshooting

Reinstall backend dependencies:
```bash
pip install -r requirements.txt
```

Reinstall frontend packages:
```bash
npm install
```

Install desktop requirements manually:
```bash
pip install PyQt5 matplotlib
```

---
