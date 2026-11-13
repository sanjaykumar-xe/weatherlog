import AirQuality from "../components/AirQuality.jsx";
import CurrentWeather from "../components/CurrentWeather.jsx";
import Forecast from "../components/Forecast.jsx";
import LocationSearch from "../components/LocationSearch.jsx";
import LocationSummary from "../components/LocationSummary.jsx";
import { InfoMessage } from "../components/Messages.jsx";
import TravelerInsights from "../components/TravelerInsights.jsx";
import useRequest from "../hooks/useRequest.js";
import { getAirQuality, getCurrentWeather, getForecast } from "../services/api.js";

export default function DashboardPage({ location, onSelectLocation }) {
  // each panel loads on its own so one provider failure never blocks the others
  const current = useRequest(location ? () => getCurrentWeather(location) : null, [location]);
  const forecast = useRequest(location ? () => getForecast(location) : null, [location]);
  const airQuality = useRequest(location ? () => getAirQuality(location) : null, [location]);

  return (
    <>
      <LocationSearch selectedLocation={location} onSelect={onSelectLocation} />
      {!location && (
        <InfoMessage>Select a location to see current weather, a five-day forecast and air quality.</InfoMessage>
      )}
      {location && (
        <>
          <LocationSummary location={location} />
          <div className="grid">
            <CurrentWeather request={current} />
            <AirQuality request={airQuality} />
          </div>
          <TravelerInsights
            currentRequest={current}
            forecastRequest={forecast}
            airQualityRequest={airQuality}
          />
          <Forecast request={forecast} />
        </>
      )}
    </>
  );
}
