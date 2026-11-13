import { formatLocalTime, formatValue, formatWind } from "../utils/format.js";
import { describeWeather } from "../utils/weatherCodes.js";
import AsyncContent from "./AsyncContent.jsx";
import StatList from "./StatList.jsx";
import WeatherIcon from "./WeatherIcon.jsx";

export default function CurrentWeather({ request }) {
  return (
    <section className="panel" aria-labelledby="current-heading">
      <h2 id="current-heading">Current weather</h2>
      <AsyncContent request={request} loadingText="Loading current weather…">
        {(data) => {
          const condition = describeWeather(data.weather_code, data.is_day !== 0);
          const { units } = data;
          return (
            <>
              <div className="current-main">
                <WeatherIcon condition={condition} large />
                <div>
                  <p className="temperature">{formatValue(data.temperature, units.temperature)}</p>
                  <p>{condition.label}</p>
                </div>
              </div>
              <StatList
                items={[
                  { label: "Feels like", value: formatValue(data.apparent_temperature, units.temperature) },
                  { label: "Humidity", value: formatValue(data.humidity, units.humidity, 0) },
                  { label: "Wind", value: formatWind(data.wind_speed, data.wind_direction, units.wind_speed) },
                  { label: "Precipitation", value: formatValue(data.precipitation, units.precipitation) },
                  { label: "Cloud cover", value: formatValue(data.cloud_cover, units.cloud_cover, 0) },
                ]}
              />
              <p className="note">
                Latest model reading for this location, valid at {formatLocalTime(data.time)} (local time, {data.timezone}).
              </p>
            </>
          );
        }}
      </AsyncContent>
    </section>
  );
}
