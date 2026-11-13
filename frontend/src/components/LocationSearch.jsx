import { useId, useState } from "react";
import { searchLocations } from "../services/api.js";
import { formatLocation } from "../utils/format.js";
import { ErrorMessage, InfoMessage } from "./Messages.jsx";

const GEOLOCATION_MESSAGES = {
  1: "Location permission was denied. Allow access in your browser settings, or search for a place instead.",
  2: "Your location is unavailable right now. Search for a place instead.",
  3: "Finding your location took too long. Try again, or search for a place instead.",
};

const roundCoordinate = (value) => Math.round(value * 10000) / 10000;
const isSameLocation = (a, b) => Boolean(a && b) && a.latitude === b.latitude && a.longitude === b.longitude;

export default function LocationSearch({ selectedLocation, onSelect }) {
  const inputId = useId();
  const [text, setText] = useState("");
  const [search, setSearch] = useState({ status: "idle", query: "", results: [], message: "" });
  const [locating, setLocating] = useState(false);
  const [geolocationError, setGeolocationError] = useState("");
  const busy = search.status === "loading" || locating;

  async function handleSubmit(event) {
    event.preventDefault();
    const query = text.trim();
    setGeolocationError("");
    if (!query) {
      setSearch({ status: "error", query, results: [], message: "Enter a city, town or postal code to search." });
      return;
    }
    setSearch({ status: "loading", query, results: [], message: "" });
    try {
      const results = await searchLocations(query);
      setSearch({ status: "done", query, results, message: "" });
    } catch (error) {
      setSearch({ status: "error", query, results: [], message: error.message });
    }
  }

  function handleUseMyLocation() {
    setGeolocationError("");
    if (!navigator.geolocation) {
      setGeolocationError("Your browser does not support location access. Search for a place instead.");
      return;
    }
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        const latitude = roundCoordinate(coords.latitude);
        const longitude = roundCoordinate(coords.longitude);
        setLocating(false);
        setSearch({ status: "idle", query: "", results: [], message: "" });
        onSelect({ name: `My location (${latitude}, ${longitude})`, admin_area: null, country: null, latitude, longitude });
      },
      (error) => {
        setLocating(false);
        setGeolocationError(GEOLOCATION_MESSAGES[error.code] ?? "Could not get your location. Search for a place instead.");
      },
      { timeout: 10000, maximumAge: 60000 }
    );
  }

  return (
    <section className="panel" aria-labelledby={`${inputId}-heading`}>
      <h2 id={`${inputId}-heading`}>Find a location</h2>
      <form onSubmit={handleSubmit} role="search">
        <label htmlFor={inputId}>City, town, postal code or place name</label>
        <div className="row">
          <input
            id={inputId}
            type="search"
            value={text}
            maxLength={100}
            onChange={(event) => setText(event.target.value)}
            aria-invalid={search.status === "error"}
            aria-describedby={`${inputId}-feedback`}
          />
          <button type="submit" disabled={busy}>
            {search.status === "loading" ? "Searching…" : "Search"}
          </button>
        </div>
      </form>
      <div className="row">
        <button type="button" className="button-secondary" onClick={handleUseMyLocation} disabled={busy}>
          {locating ? "Finding your location…" : "Use my location"}
        </button>
        <span className="hint">Your browser will ask for permission. Searching by name always works.</span>
      </div>

      <div id={`${inputId}-feedback`}>
        {geolocationError && <ErrorMessage message={geolocationError} />}
        {search.status === "loading" && <p role="status">Searching for “{search.query}”…</p>}
        {search.status === "error" && <ErrorMessage message={search.message} />}
        {search.status === "done" && search.results.length === 0 && (
          <InfoMessage>No places found for “{search.query}”. Check the spelling or try a nearby city or postal code.</InfoMessage>
        )}
        {search.status === "done" && search.results.length > 0 && (
          <>
            <p>
              {search.results.length} {search.results.length === 1 ? "match" : "matches"} found. Select the place you want.
            </p>
            <ul className="result-list">
              {search.results.map((result) => (
                <li key={`${result.latitude},${result.longitude},${result.name}`}>
                  <button
                    type="button"
                    className="result-button"
                    aria-pressed={isSameLocation(result, selectedLocation)}
                    onClick={() => onSelect(result)}
                  >
                    <span className="result-name">{formatLocation(result)}</span>
                    <span className="hint">
                      {result.latitude.toFixed(2)}, {result.longitude.toFixed(2)}
                      {result.timezone ? ` · ${result.timezone}` : ""}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </>
        )}
      </div>
    </section>
  );
}
