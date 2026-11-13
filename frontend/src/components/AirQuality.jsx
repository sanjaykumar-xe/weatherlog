import { formatLocalTime, formatValue } from "../utils/format.js";
import AsyncContent from "./AsyncContent.jsx";
import StatList from "./StatList.jsx";

// standard US AQI categories
function usAqiCategory(value) {
  if (value === null || value === undefined) return "";
  if (value <= 50) return " (Good)";
  if (value <= 100) return " (Moderate)";
  if (value <= 150) return " (Unhealthy for sensitive groups)";
  if (value <= 200) return " (Unhealthy)";
  if (value <= 300) return " (Very unhealthy)";
  return " (Hazardous)";
}

export default function AirQuality({ request }) {
  return (
    <section className="panel" aria-labelledby="air-quality-heading">
      <h2 id="air-quality-heading">Air quality</h2>
      <AsyncContent request={request} loadingText="Loading air quality…">
        {(data) => (
          <>
            <StatList
              items={[
                { label: "PM2.5", value: formatValue(data.pm2_5, data.units.pm2_5) },
                { label: "PM10", value: formatValue(data.pm10, data.units.pm10) },
                {
                  label: "US AQI",
                  value:
                    data.us_aqi === null || data.us_aqi === undefined
                      ? "Not available here"
                      : `${formatValue(data.us_aqi, "", 0)}${usAqiCategory(data.us_aqi)}`,
                },
              ]}
            />
            <p className="note">
              Model-based estimates from Open-Meteo for {formatLocalTime(data.time)} local time, not readings from a
              nearby sensor. AQI is the United States scale, not a national index of another country.
            </p>
          </>
        )}
      </AsyncContent>
    </section>
  );
}
