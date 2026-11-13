const MISSING = "—";
const COMPASS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"];

export function formatLocation(location) {
  return [location.name, location.admin_area, location.country].filter(Boolean).join(", ");
}

export function formatValue(value, unit = "", digits = 1) {
  if (value === null || value === undefined) return MISSING;
  const factor = 10 ** digits;
  const rounded = Math.round(value * factor) / factor;
  if (!unit) return String(rounded);
  return unit === "%" ? `${rounded}%` : `${rounded} ${unit}`;
}

export function formatWind(speed, direction, unit) {
  if (speed === null || speed === undefined) return MISSING;
  if (direction === null || direction === undefined) return formatValue(speed, unit);
  const compass = COMPASS[Math.round(direction / 45) % 8];
  return `${formatValue(speed, unit)} from ${compass} (${direction}°)`;
}

// provider dates have no time zone, so format them as UTC to avoid shifting the day
export function formatDay(isoDate) {
  return new Date(`${isoDate}T00:00:00Z`).toLocaleDateString(undefined, {
    weekday: "short",
    day: "numeric",
    month: "short",
    timeZone: "UTC",
  });
}

export function formatLocalTime(isoLocalTime) {
  if (!isoLocalTime) return MISSING;
  return new Date(`${isoLocalTime}Z`).toLocaleString(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
  });
}

export function formatDateTime(isoTimestamp) {
  return new Date(isoTimestamp).toLocaleString();
}
