export default function WeatherIcon({ condition, large = false }) {
  return (
    <span className={large ? "weather-icon weather-icon-large" : "weather-icon"} role="img" aria-label={condition.label}>
      {condition.icon}
    </span>
  );
}
