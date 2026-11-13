// keep these in sync with MAX_RANGE_DAYS and EARLIEST_DATE in backend/app/config.py
export const MAX_RANGE_DAYS = 92;
export const EARLIEST_DATE = "1940-01-01";

const DAY_MS = 24 * 60 * 60 * 1000;

// the backend compares against the current UTC date
export const todayIso = () => new Date().toISOString().slice(0, 10);

function parseIsoDate(value) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return null;
  const date = new Date(`${value}T00:00:00Z`);
  return Number.isNaN(date.getTime()) || date.toISOString().slice(0, 10) !== value ? null : date;
}

// returns an error message, or null when the range is valid
export function validateDateRange(start, end) {
  if (!start || !end) return "Choose both a start date and an end date.";
  const startDate = parseIsoDate(start);
  const endDate = parseIsoDate(end);
  if (!startDate || !endDate) return "Enter dates in the format YYYY-MM-DD.";
  if (startDate > endDate) return "The start date must not be after the end date.";
  if (start < EARLIEST_DATE) return `Historical data starts on ${EARLIEST_DATE}.`;
  if (end > todayIso()) return "Historical searches cannot include future dates.";
  if ((endDate - startDate) / DAY_MS + 1 > MAX_RANGE_DAYS) {
    return `The date range cannot be longer than ${MAX_RANGE_DAYS} days.`;
  }
  return null;
}
