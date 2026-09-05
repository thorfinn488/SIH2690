# SIH 26090 - AI-Driven Market Linkage & Smart Cataloging Backend

This repository contains the complete `/backend` service for the SIH 26090 project: **"AI-Driven Market Linkage and Smart Cataloging Mobile Application for Marginalized Artisans"**.

## Technical Stack
- **Language/Framework**: Python 3.11+, FastAPI
- **ORM**: SQLAlchemy (supports PostgreSQL / Supabase & SQLite)
- **Validation**: Pydantic v2 schemas
- **Auth**: PyJWT (HS256) & bcrypt password hashing
- **File Storage**: Abstract storage interface (`local` disk or `supabase` storage)
- **Image Enhancement**: Pillow-based local enhancement in the mock AI boundary; original and enhanced assets are persisted
- **Background Jobs**: FastAPI `BackgroundTasks`
- **Testing**: `pytest`

---

## Folder Structure
```
backend/
├── app/
│   ├── main.py                     # FastAPI application entrypoint & middleware
│   ├── config/
│   │   └── settings.py             # Environment configuration (Pydantic Settings)
│   ├── api/
│   │   └── v1/                     # API routes (auth, products, dashboard, admin)
│   ├── models/                     # SQLAlchemy database ORM models (11 models)
│   ├── schemas/                    # Pydantic request/response schemas & envelopes
│   ├── services/                   # Business logic layer (auth, product, pipeline, dashboard)
│   ├── repositories/               # Data access repository layer
│   ├── middleware/                 # Auth JWT dependency, error handler, rate limiting
│   ├── auth/                       # Password hashing, JWT token handlers, RBAC
│   ├── ai_mocks/                   # AI service mock layer with standard signatures
│   ├── storage/                    # Abstract storage layer (local & Supabase)
│   └── utils/                      # File validation & audit logging helpers
├── tests/                          # Pytest suite (pricing, auth, product ownership)
├── scripts/                        # Database seed script with realistic Indian craft data
├── docs/                           # Documentation (API specs, database schema, AI pipeline)
├── .env.example
├── requirements.txt
└── README.md
```

---

## Setup & Running Instructions

The project uses a single repository root containing both applications:
```text
sih26090/
├── backend/   # FastAPI API, database, AI services, and tests
└── frontend/  # React/Vite web application
```

After the frontend is built, FastAPI serves `frontend/dist` from `/`, while all API routes remain under `/api`. This allows the production build to run from one backend process without a separate frontend server.

### 1. Environment Setup
Create a virtual environment and install dependencies:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default local configuration uses SQLite (`sqlite:///./sih26090.db`). The SQLAlchemy schema already persists users, artisans, products, uploaded assets, catalogues, pricing, opportunities, insights, and audit logs. For Supabase PostgreSQL, set `DATABASE_URL` to your Supabase connection string.

### 3. Run Database Seed Script
Populate the database with realistic artisans, products (Phulkari, Madhubani, Bamboo craft, Wooden handicrafts), buyers, market opportunities, and AI insights:
```bash
python scripts/seed_data.py
```

### 4. Start Development Server
```bash
python -m uvicorn app.main:app --reload --port 8000
```
Interactive API Documentation will be available at:
- OpenAPI / Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 5. Build and Connect the Frontend
From the repository root:
```bash
cd frontend
npm install
npm run build
cd ../backend
python -m uvicorn app.main:app --reload --port 8000
```
Open `http://localhost:8000/` for the React application. During frontend development, `npm run dev` starts Vite on port 3000 and proxies `/api` and `/static` to the backend on port 8000.

---

## Running Unit Tests
Execute the pytest suite:
```bash
python -m pytest tests/
```

---

## Detailed Documentation
For detailed module specifications:
- [API Documentation](file:///C:/Users/drsen/.gemini/antigravity/scratch/sih26090/backend/docs/api.md)
- [Database Schema Documentation](file:///C:/Users/drsen/.gemini/antigravity/scratch/sih26090/backend/docs/database.md)
- [AI Pipeline Integration Guide](file:///C:/Users/drsen/.gemini/antigravity/scratch/sih26090/backend/docs/ai-pipeline.md)
