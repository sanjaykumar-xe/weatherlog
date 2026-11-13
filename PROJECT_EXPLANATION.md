# WeatherLog — Project Technical Explanation & Architecture Walkthrough

**Applicant:** Sanjay Kumar  
**Target Role:** AI Engineer Intern (AI / ML / GenAI Application)  
**Company:** Product Manager Accelerator (PM Accelerator)  
**Repository:** [https://github.com/sanjaykumar-xe/weatherlog](https://github.com/sanjaykumar-xe/weatherlog)  
**Track:** Full-Stack Submission (Tech Assessment #1 & #2)

---

## 1. Executive Summary

WeatherLog is a full-stack weather intelligence and observation management application designed to solve real-world traveler and planning problems. Rather than presenting generic current readings, WeatherLog combines real-time weather metrics, multi-day forecasting, atmospheric air quality indices, and non-obvious travel considerations into a resilient, responsive interface backed by a persistent SQLite database with full CRUD capabilities and data export engines.

The platform was built from the ground up to satisfy 100% of the requirements for both **Tech Assessment #1 (Frontend)** and **Tech Assessment #2 (Backend)**, securing the highest priority full-stack evaluation criteria.

---

## 2. User-Centric Problem Statement: Thinking Like a Traveler

The assessment prompt highlights:
> *"What are some things they should consider that might not be obvious? We want you to think like a user who needs to know the weather in their current location or another location of interest they hope to be traveling to."*

When traveling, travelers frequently encounter weather pitfalls that single-number forecasts fail to convey:
1. **The Diurnal Temperature Trap:** A destination with a pleasant $24^\circ\text{C}$ high might drop to $10^\circ\text{C}$ after sunset, leaving travelers unprepared without evening layers.
2. **Apparent Temperature vs. Thermometer Reading:** Strong winds cause chilling evaporation, while high relative humidity prevents cooling, making conditions feel drastically different from the ambient thermometer reading.
3. **Micro-Precipitation & Rain Probabilities:** A day might look sunny overall, yet carry an 80% localized afternoon rain probability.
4. **Air Quality & Respiratory Sensitivities:** High PM2.5 or ozone levels directly impact travelers planning outdoor running, hiking, or sightseeing.

### How WeatherLog Solves This:
WeatherLog incorporates a dedicated **Traveler Considerations & Insights** engine that actively synthesizes multi-variable data:
- **Diurnal Swing Alert:** Triggers whenever high/low spread is $\ge 8^\circ\text{C}$, warning the traveler to pack versatile base layers and an evening jacket.
- **Wind Chill / Heat Index Advisory:** Detects deviations $\ge 3^\circ\text{C}$ between ambient and apparent temperatures.
- **Rain Gear Recommendations:** Evaluates current precipitation and multi-day rain probabilities ($\ge 30\%$).
- **Health Advisories:** Flags elevated US AQI ($>50$) and particulate concentrations (PM2.5/PM10) for sensitive groups.

---

## 3. High-Level System Architecture

The application adopts a decoupled client-server architecture:

```
[ Browser / Client ] 
       │
       ▼ (HTTP / JSON)
[ React 18 + Vite SPA ]  (:5173)
       │
       ▼ (REST API / CORS)
[ FastAPI Backend Gateway ]  (:8000)
       ├── Business Validations (Lat/Lon Bounds, Date Ranges <= 92 Days)
       ├── HTTPX Async Provider Client (Timeouts, 429 Rate Limiting)
       ├── SQLModel ORM (SQLite with PRAGMA foreign_keys=ON)
       └── Export Stream Engine (RFC-4180 CSV & JSON)
       │
       ├──► [ Open-Meteo Live APIs ] (Geocoding, Forecast, Archive, Air Quality)
       └──► [ SQLite Database ] (weather_records & weather_observations with CASCADE)
```

---

## 4. Requirement-by-Requirement Mapping

### Tech Assessment #1 (Frontend)
| Requirement | Implementation Detail | Source File |
|---|---|---|
| **Location Input** | City, town, postal/zip code, landmarks via live geocoding autocomplete | `src/components/LocationSearch.jsx` |
| **Current Location** | Browser Geolocation API integration with permission handling | `src/components/LocationSearch.jsx` |
| **Current Weather Details** | Temp, feels-like, wind speed & direction, humidity, precipitation, cloud cover | `src/components/CurrentWeather.jsx` |
| **Weather Icons & Visuals** | Standardized WMO weather code mapping to semantic icon badges | `src/components/WeatherIcon.jsx`, `src/utils/weatherCodes.js` |
| **5-Day Forecast (1.1)** | High/low temperatures, precipitation total and probability, max wind speed | `src/components/Forecast.jsx` |
| **Graceful Error Handling (1.2)** | Isolated async loading cards; air quality failures never block weather or forecast panels | `src/components/AsyncContent.jsx`, `src/hooks/useRequest.js` |
| **Responsive Design** | Pure CSS grid and flexbox layout adapting to smartphones, tablets, and desktops | `src/styles/main.css` |
| **Company Description & Name** | Dedicated tab and persistent footer with PM Accelerator description & Sanjay Kumar | `src/pages/AboutPage.jsx`, `src/App.jsx` |

### Tech Assessment #2 (Backend)
| Requirement | Implementation Detail | Source File |
|---|---|---|
| **Database Persistence** | SQLite relational database with SQLModel ORM | `app/database.py`, `app/models.py` |
| **CRUD: Create** | Validates location & date range, queries historical reanalysis data, stores record + observations | `app/routers/records.py` (`POST /api/records`) |
| **CRUD: Read** | Paginated summary listing and full detail retrieval with all child observations | `app/routers/records.py` (`GET /api/records`, `GET /api/records/{id}`) |
| **CRUD: Update** | Re-fetches fresh provider data first; only updates on success to guarantee state integrity | `app/routers/records.py` (`PUT /api/records/{id}`) |
| **CRUD: Delete** | Deletes parent record with database-level `ON DELETE CASCADE` removing observations | `app/routers/records.py` (`DELETE /api/records/{id}`) |
| **Input Validation** | Lat $[-90, 90]$, Lon $[-180, 180]$, dates $\le 92$ days, non-future dates, ISO validation | `app/validation.py`, `app/schemas.py` |
| **External API Integration (2.2)** | Open-Meteo (Geocoding, Forecast, Archive, Air Quality) + Google Maps deep link | `app/services/*.py`, `src/components/MapLink.jsx` |
| **Data Export (2.3)** | Streamed CSV and JSON file downloads with spreadsheet formula injection protection | `app/exports.py` (`GET /api/records/export`) |
| **Testing** | 87 automated test cases mocking all upstream responses (zero external network dependency) | `backend/tests/` |

---

## 5. Technical Highlights & Engineering Decisions

### 1. Cascade Deletion with Referential Integrity
In SQLite, foreign keys are disabled by default on new connections. In `app/database.py`, an event listener executes `PRAGMA foreign_keys=ON` on every connection:
```python
@event.listens_for(db_engine, "connect")
def enable_foreign_keys(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
```
This guarantees that deleting a `WeatherRecord` automatically cascades to delete all associated `WeatherObservation` entries directly at the database engine level, even outside the ORM.

### 2. Transactional Update Safety (Fetch-Before-Mutate)
In `app/routers/records.py`, when a user updates a record (`PUT /api/records/{id}`), the application queries Open-Meteo for the replacement dataset *before* opening a database transaction. If the provider is unreachable, timed out, or returns invalid data, the existing record in the database remains completely untouched.

### 3. CSV Formula Injection Defense (CSV Injection / CWE-1236)
When exporting user-supplied location names to CSV (`app/exports.py`), text values beginning with `=`, `+`, `-`, or `@` could trigger formula execution when opened in Microsoft Excel or Google Sheets. WeatherLog automatically sanitizes these fields by prepending a single quote (`'`), neutralizing potential spreadsheet exploits. An Excel-compatible UTF-8 Byte Order Mark (`\ufeff`) is also prepended to ensure international characters render correctly.

### 4. Non-Blocking Resilient UI Fetching
In `frontend/src/pages/DashboardPage.jsx`, instead of combining weather and air quality into a single fragile endpoint, independent async calls are executed via `useRequest`:
```javascript
const current = useRequest(location ? () => getCurrentWeather(location) : null, [location]);
const forecast = useRequest(location ? () => getForecast(location) : null, [location]);
const airQuality = useRequest(location ? () => getAirQuality(location) : null, [location]);
```
If the Air Quality service experiences upstream latency or rate limiting, the Current Weather and 5-Day Forecast panels continue rendering smoothly without interruption.

---

## 6. Demo Video Walkthrough Script (1–2 Minutes)

Use this script as a guide when recording your screen share:

| Timestamp | Screen | Speaking Points |
|---|---|---|
| **0:00 – 0:20** | **Dashboard** | *"Hello, my name is Sanjay Kumar, and this is my submission for the PM Accelerator AI Engineer Intern assessment. WeatherLog is a full-stack weather intelligence app built with React, FastAPI, and SQLite. Let's search for a city—like San Francisco. Notice the live current conditions, WMO weather icons, and 5-day forecast."* |
| **0:20 – 0:40** | **Traveler Insights & Air Quality** | *"Notice our Air Quality panel showing PM2.5, PM10, and US AQI. To answer the prompt about what travelers should consider that isn't obvious, our Traveler Considerations widget dynamically detects diurnal temperature swings to recommend layering, checks rain probability for packing gear, and issues air quality advisories."* |
| **0:40 – 1:05** | **Historical Search & CRUD** | *"Now let's switch to Historical Search. I'll select a date range—validated to prevent future dates and ranges over 92 days. We retrieve historical reanalysis data and click 'Save to database'. Switching to 'Saved records', we can view all stored lookups with complete daily observation breakdowns."* |
| **1:05 – 1:25** | **Updates, Cascade Delete & Export** | *"Let's test our CRUD operations: updating a record re-fetches verified provider data, while deleting a record cleanly cascades in SQLite. We can also export our entire database directly to CSV or JSON with built-in spreadsheet formula protection."* |
| **1:25 – 1:40** | **About PM Accelerator & Code** | *"Finally, our 'About PM Accelerator' tab features the company description and candidate credentials. On the backend, we maintain 87 automated tests with 100% pass rate. Thank you!"* |

---

## 7. Submission Checklist Summary

- [x] Full-Stack scope completed (Tech Assessment #1 + #2)
- [x] 87 Pytest unit & integration tests passing offline
- [x] Production build tested and verified (`npm run build`)
- [x] Candidate name (**Sanjay Kumar**) configured in code and UI
- [x] Product Manager Accelerator company description included
- [x] Code pushed to GitHub: [https://github.com/sanjaykumar-xe/weatherlog](https://github.com/sanjaykumar-xe/weatherlog)
- [x] Ready for Google Form submission

