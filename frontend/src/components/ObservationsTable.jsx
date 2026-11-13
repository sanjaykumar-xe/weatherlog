import { formatDay, formatValue } from "../utils/format.js";
import { describeWeather } from "../utils/weatherCodes.js";
import WeatherIcon from "./WeatherIcon.jsx";

const VALUE_FIELDS = ["temperature_min", "temperature_max", "temperature_mean", "precipitation_sum", "wind_speed_max", "weather_code"];

export default function ObservationsTable({ observations, dataset }) {
  const daysWithoutData = observations.filter((row) => VALUE_FIELDS.every((field) => row[field] === null)).length;
  return (
    <div>
      <p className="note">
        Historical reanalysis/model data{dataset ? ` (${dataset})` : ""}. These are not direct measurements from a weather
        station at this exact point.
      </p>
      {daysWithoutData > 0 && (
        <p className="note">
          {daysWithoutData} {daysWithoutData === 1 ? "day has" : "days have"} no published data yet and show “—”.
        </p>
      )}
      <table className="responsive-table">
        <caption className="sr-only">Daily historical weather</caption>
        <thead>
          <tr>
            <th scope="col">Date</th>
            <th scope="col">Condition</th>
            <th scope="col">Min (°C)</th>
            <th scope="col">Max (°C)</th>
            <th scope="col">Mean (°C)</th>
            <th scope="col">Precipitation (mm)</th>
            <th scope="col">Max wind (km/h)</th>
          </tr>
        </thead>
        <tbody>
          {observations.map((row) => {
            const condition = row.weather_code === null ? null : describeWeather(row.weather_code);
            return (
              <tr key={row.observation_date}>
                <th scope="row" data-label="Date">
                  {formatDay(row.observation_date)}
                </th>
                <td data-label="Condition">
                  {condition ? (
                    <>
                      <WeatherIcon condition={condition} /> {condition.label}
                    </>
                  ) : (
                    "—"
                  )}
                </td>
                <td data-label="Min (°C)">{formatValue(row.temperature_min)}</td>
                <td data-label="Max (°C)">{formatValue(row.temperature_max)}</td>
                <td data-label="Mean (°C)">{formatValue(row.temperature_mean)}</td>
                <td data-label="Precipitation (mm)">{formatValue(row.precipitation_sum)}</td>
                <td data-label="Max wind (km/h)">{formatValue(row.wind_speed_max)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
