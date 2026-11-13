import { formatLocation } from "../utils/format.js";
import MapLink from "./MapLink.jsx";

export default function LocationSummary({ location }) {
  return (
    <div className="location-summary">
      <h2>{formatLocation(location)}</h2>
      <p>
        {location.latitude.toFixed(4)}, {location.longitude.toFixed(4)} · <MapLink location={location} />
      </p>
    </div>
  );
}
