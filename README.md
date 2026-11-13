# WeatherLog

WeatherLog is a full-stack weather intelligence and observation logging platform built for the **Product Manager Accelerator (PM Accelerator) AI Engineer Intern Technical Assessment** by **Sanjay Kumar**.

It implements both **Tech Assessment #1 (Frontend)** and **Tech Assessment #2 (Backend)** to deliver a production-grade Full Stack submission.

> 📖 **Project Walkthrough & Demo Guide:** See [PROJECT_EXPLANATION.md](PROJECT_EXPLANATION.md) for detailed technical decisions, architecture rationale, and the 1–2 minute demo video script.

---

## About Product Manager Accelerator

**Product Manager Accelerator** is a premier global learning community and career accelerator designed to help aspiring and experienced professionals break into and excel in Product Management, AI, and Technology roles. Through hands-on mentorship, end-to-end industry training, and real-world project development experience, PM Accelerator empowers candidates to build high-impact applications and accelerate their career growth.

- LinkedIn: [Product Manager Accelerator](https://www.linkedin.com/company/product-manager-accelerator/)

---

## Features & Assessment Coverage

### Tech Assessment #1: Frontend Capabilities
- **Flexible Location Input:** Search by city, town, postal/zip code, landmarks, or coordinates via live geocoding.
- **Current Location (Geolocation API):** Quick "Use my location" button with browser permission handling and fallbacks.
- **Current Conditions & Weather Icons:** Temperature, feels-like, humidity, wind speed & direction, precipitation, cloud cover, and WMO-standard condition icons.
- **Five-Day Forecast (1.1):** High/low temperatures, precipitation probability/sum, maximum wind speed, and weather condition badges.
- **Traveler Considerations & Non-Obvious Insights:** Smart rules assessing temperature variations (layering advice), precipitation likelihood (rain gear alerts), wind chill, and air quality health advisories for travelers.
- **Graceful Error Handling (1.2):** Non-blocking isolated cards (e.g., air quality failure never blocks weather or forecast), network disconnection notices, and input validation warnings.
- **Responsive Web-First Design:** Fluid CSS grid and flexbox layout adapting to smartphones, tablets, and desktops.

### Tech Assessment #2: Backend & Database Capabilities
- **Persistence & Full CRUD (2.1):**
  - **Create:** Query historical daily weather by location and date range, validate range limits, and persist the record with individual daily observations.
  - **Read:** Fetch summary lists (paginated) or inspect full record history and observations.
  - **Update:** Modify existing records (updates re-fetch validated provider data before touching the database).
  - **Delete:** Remove records with cascade deletion (`ON DELETE CASCADE`) removing child observations.
- **API Integration & Value Adds (2.2):**
  - **Open-Meteo Weather & Geocoding APIs** (CC BY 4.0, zero hardcoded data).
  - **Open-Meteo Air Quality API** (PM2.5, PM10, US AQI scale).
  - **Google Maps Navigation:** Direct link to inspect coordinates on Google Maps.
- **Data Export (2.3):**
  - Full database exports streamed directly as **CSV** or **JSON**. Spreadsheet formula injection protection included.
- **Input & Business Rule Validation:**
  - Latitude (-90 to 90), longitude (-180 to 180).
  - Date ranges restricted to valid calendar windows, non-future dates, and maximum 92-day spans.

---

## Tech Stack

| Area | Technology |
|---|---|
| **Frontend** | React 18, Vite, JavaScript (JSX), Vanilla CSS, Fetch API |
| **Backend** | Python 3.10+, FastAPI, Uvicorn, HTTPX |
| **Database** | SQLite via SQLModel (SQLAlchemy + Pydantic) |
| **Testing** | Pytest (87 offline unit & integration tests with mocked HTTP transport) |
| **APIs** | Open-Meteo Geocoding, Forecast, Historical Archive, and Air Quality |

---

## Project Structure

```text
WeatherLog/
├── backend/
│   ├── app/
│   │   ├── routers/        # locations.py, weather.py, records.py
│   │   ├── services/       # client.py, geocoding.py, weather.py, air_quality.py
│   │   ├── config.py       # Configuration & environment settings
│   │   ├── database.py     # Engine & session management (foreign keys enabled)
│   │   ├── models.py       # SQLModel database tables (WeatherRecord, WeatherObservation)
│   │   ├── schemas.py      # Pydantic serialization models & validation
│   │   ├── errors.py       # Centralized application exceptions
│   │   ├── validation.py   # Coordinate & date range business rules
│   │   ├── exports.py      # CSV and JSON export builders
│   │   └── main.py         # FastAPI application entrypoint & middleware
│   ├── tests/              # 87 automated test cases
│   ├── pytest.ini
│   └── requirements.txt
├── docs/                   # Assessment specifications & references
├── frontend/
│   ├── src/
│   │   ├── components/     # UI components (CurrentWeather, Forecast, AirQuality, TravelerInsights, etc.)
│   │   ├── pages/          # DashboardPage, HistoricalPage, SavedPage, AboutPage
│   │   ├── hooks/          # useRequest data-fetching hook
│   │   ├── services/       # api.js API client
│   │   ├── styles/         # main.css responsive styling
│   │   └── utils/          # dates, formatting, weather codes
│   ├── package.json
│   └── vite.config.js
├── .env.example
├── .gitignore
└── README.md
```

---

## Local Setup & Running

### 1. Clone & Environment Configuration

```bash
git clone <repository-url> WeatherLog
cd WeatherLog
cp .env.example .env
```

Your `.env` file at the root configures both frontend and backend:
```env
DATABASE_URL=sqlite:///./weatherlog.db
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
PROVIDER_TIMEOUT_SECONDS=10
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APPLICANT_NAME=Sanjay Kumar
```

### 2. Run Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --env-file ../.env
```

The API will be available at `http://localhost:8000`. Interactive documentation is available at `http://localhost:8000/docs`.

### 3. Run Frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

The React web application will start at `http://localhost:5173`.

---

## Deployment to Vercel

WeatherLog includes native configuration for one-click deployment on [Vercel](https://vercel.com):

1. Go to [vercel.com/new](https://vercel.com/new) and import your repository (`sanjaykumar-xe/weatherlog`).
2. Leave the **Root Directory** as default (repository root); Vercel will automatically read `vercel.json`.
3. Add Environment Variables in the Vercel dashboard:
   - `VITE_APPLICANT_NAME`: `Sanjay Kumar`
4. Click **Deploy**. Vercel builds the React frontend and deploys the FastAPI backend as serverless functions under a single URL!

---

## Running the Automated Test Suite

The backend test suite contains 87 tests covering health checks, geocoding, error handling, date boundaries, database persistence across restarts, cascade deletion, and CSV/JSON exports without requiring live internet access:

```bash
cd backend
pytest
```

---

## Verification & Demo Checklist

- [x] All 87 pytest test cases passing
- [x] Responsive layout verified on desktop, tablet, and mobile breakpoints
- [x] Live Open-Meteo API integrations for Geocoding, Forecast, Air Quality, and Historical weather
- [x] Full CRUD operations on SQLite database with foreign keys and cascade delete
- [x] CSV and JSON file exports verified
- [x] Traveler considerations and non-obvious trip insights active
- [x] "About PM Accelerator" tab and candidate attribution included

---

## Author & Submission Info

- **Candidate:** Sanjay Kumar
- **Target Position:** AI Engineer Intern (AI / ML / GenAI Application)
- **Company:** Product Manager Accelerator (PM Accelerator)
