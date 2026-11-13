import { formatDay, formatValue } from "../utils/format.js";
import { describeWeather } from "../utils/weatherCodes.js";
import AsyncContent from "./AsyncContent.jsx";
import WeatherIcon from "./WeatherIcon.jsx";

export default function Forecast({ request }) {
  return (
    <section className="panel" aria-labelledby="forecast-heading">
      <h2 id="forecast-heading">Five-day forecast</h2>
      <AsyncContent request={request} loadingText="Loading forecast…">
        {({ days, units }) => (
          <ol className="forecast">
            {days.map((day) => {
              const condition = describeWeather(day.weather_code);
              return (
                <li key={day.date} className="forecast-day">
                  <h3>{formatDay(day.date)}</h3>
                  <WeatherIcon condition={condition} large />
                  <p>{condition.label}</p>
                  <p>
                    <span className="sr-only">High </span>
                    <strong>{formatValue(day.temperature_max, units.temperature)}</strong>
                    <span className="sr-only">, low </span> / {formatValue(day.temperature_min, units.temperature)}
                  </p>
                  <p>
                    Rain: {formatValue(day.precipitation_sum, units.precipitation)}
                    {day.precipitation_probability_max !== null && day.precipitation_probability_max !== undefined
                      ? ` (${day.precipitation_probability_max}% chance)`
                      : ""}
                  </p>
                  <p>Wind up to {formatValue(day.wind_speed_max, units.wind_speed)}</p>
                </li>
              );
            })}
          </ol>
        )}
      </AsyncContent>
    </section>
  );
}
