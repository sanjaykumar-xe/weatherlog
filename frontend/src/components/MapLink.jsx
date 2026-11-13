export default function MapLink({ location }) {
  const url = `https://www.google.com/maps/search/?api=1&query=${location.latitude},${location.longitude}`;
  return (
    <a href={url} target="_blank" rel="noopener noreferrer">
      View on Google Maps
    </a>
  );
}
