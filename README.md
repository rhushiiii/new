# PowerGuard - Electricity Theft Detection System

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React"/>
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="Scikit-learn"/>
</p>

PowerGuard is an ML-powered full-stack web application for detecting electricity theft and abnormal household energy usage patterns in smart meter data.

## 🌟 Features

- **CSV Data Upload** - Upload smart meter consumption data
- **ML Anomaly Detection** - Isolation Forest & Autoencoder models
- **Real-time Dashboard** - Monitor meters and risk levels
- **Interactive Analytics** - Visualize consumption patterns
- **Explainable AI** - Understand why meters are flagged
- **Risk Classification** - Critical, High, Medium, Low levels

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, SQLAlchemy, Pydantic |
| ML | scikit-learn (Isolation Forest), TensorFlow (Autoencoder) |
| Database | PostgreSQL / SQLite |
| Frontend | React 18, Vite, Recharts |
| Styling | Custom CSS Design System |
| Deployment | Docker, Render/Railway, Vercel |

## 📁 Project Structure

```
project4/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── config.py         # Settings
│   │   ├── database.py       # DB connection
│   │   ├── models/           # SQLAlchemy models
│   │   ├── routers/          # API endpoints
│   │   ├── services/         # Business logic
│   │   └── ml/               # ML models
│   ├── scripts/
│   │   └── generate_mock_data.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/       # UI components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API client
│   │   └── hooks/            # Custom hooks
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL (optional, SQLite works for development)

### Local Development

#### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload
```

Backend will be available at: http://localhost:8000
API Docs (Swagger): http://localhost:8000/docs

#### 2. Generate Mock Data

```bash
cd backend/scripts
python generate_mock_data.py --meters 50 --days 30
```

This creates `mock_meter_data.csv` with realistic consumption patterns and anomalies.

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at: http://localhost:5173

### Docker Deployment

```bash
# Build and run all services
docker-compose up --build

# Access the application
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 📊 API Endpoints

### Upload
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/upload/data` | Upload CSV file |
| POST | `/api/v1/upload/clear` | Clear all data |

### Anomaly Detection
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/anomaly/detect` | Run detection |
| GET | `/api/v1/anomaly/results` | Get all results |
| GET | `/api/v1/anomaly/stats` | Dashboard stats |

### Meters
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/meters/` | List all meters |
| GET | `/api/v1/meters/{id}` | Get meter time series |
| GET | `/api/v1/meters/{id}/analysis` | Detailed analysis |

## 🧠 ML Models

### Isolation Forest (Default)
- Unsupervised anomaly detection
- Works well with high-dimensional data
- Fast training and prediction

### Autoencoder (Optional)
- Neural network-based
- Learns normal consumption patterns
- Detects anomalies via reconstruction error

### Features Extracted
- **Hourly Average** - Average consumption per hour
- **Daily Variance** - Consumption variability
- **Night Ratio** - Night-time usage proportion
- **Peak Ratio** - Peak hour consumption
- **Weekend Ratio** - Weekend vs weekday usage

## 🎯 Usage Demo

### Step 1: Upload Data
1. Navigate to Upload page
2. Drag & drop or select CSV file
3. Click "Upload Data"

### Step 2: Run Detection
1. Click "Run Anomaly Detection"
2. Choose model (Isolation Forest / Autoencoder)
3. View results on Dashboard

### Step 3: Analyze Results
1. Check Dashboard for overview
2. Use Risk Table for detailed view
3. Use Analytics for individual meter analysis

## 📈 CSV Format

```csv
meter_id,timestamp,consumption_kwh
METER_0001,2024-01-15T00:00:00,0.85
METER_0001,2024-01-15T01:00:00,0.72
METER_0002,2024-01-15T00:00:00,1.23
```

## 🚢 Deployment

### Backend (Render/Railway)

1. Create new Web Service
2. Connect to GitHub repository
3. Set root directory: `backend`
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables:
   ```
   DATABASE_URL=postgresql://...
   USE_SQLITE=false
   CORS_ORIGINS=https://your-frontend.vercel.app
   ```

### Frontend (Vercel)

1. Import project from GitHub
2. Set root directory: `frontend`
3. Framework preset: Vite
4. Add environment variable:
   ```
   VITE_API_URL=https://your-backend.onrender.com
   ```

## 🔧 Configuration

### Environment Variables

#### Backend
| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | - | PostgreSQL connection URL |
| `USE_SQLITE` | `true` | Use SQLite for development |
| `CORS_ORIGINS` | `localhost` | Allowed origins |
| `ANOMALY_THRESHOLD` | `0.5` | Detection threshold |
| `ISOLATION_FOREST_CONTAMINATION` | `0.1` | Expected anomaly rate |

## 📝 License

MIT License - feel free to use this project for learning, demos, or production!

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a PR.

---

<p align="center">
  Built with ❤️ for the hackathon community
</p>
