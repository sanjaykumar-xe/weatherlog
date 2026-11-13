import os
from datetime import date

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./weatherlog.db")
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]
PROVIDER_TIMEOUT_SECONDS = float(os.getenv("PROVIDER_TIMEOUT_SECONDS", "10"))

# Historical search limits; the frontend mirrors these in src/utils/dates.js
MAX_RANGE_DAYS = 92
EARLIEST_DATE = date(1940, 1, 1)
