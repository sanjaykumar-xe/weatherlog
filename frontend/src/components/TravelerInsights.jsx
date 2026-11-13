export default function TravelerInsights({ currentRequest, forecastRequest, airQualityRequest }) {
  const current = currentRequest?.data;
  const forecast = forecastRequest?.data;
  const airQuality = airQualityRequest?.data;

  if (!current && !forecast && !airQuality) {
    return null;
  }

  const considerations = [];

  // 1. Rain and gear considerations
  const rainLikely =
    (current?.precipitation && current.precipitation > 0) ||
    forecast?.days?.some((d) => (d.precipitation_probability_max ?? 0) >= 30 || (d.precipitation_sum ?? 0) > 1.0);

  if (rainLikely) {
    considerations.push({
      category: "Gear & Packing",
      title: "Rain gear recommended",
      detail: "Precipitation is either active or likely in the upcoming days. Keep a compact umbrella and water-resistant footwear handy.",
    });
  }

  // 2. Day vs night temperature variation (layering)
  if (forecast?.days?.length) {
    const maxSpread = Math.max(
      ...forecast.days
        .filter((d) => d.temperature_max != null && d.temperature_min != null)
        .map((d) => d.temperature_max - d.temperature_min),
      0
    );

    if (maxSpread >= 8) {
      considerations.push({
        category: "Clothing",
        title: "Large diurnal temperature swing",
        detail: `Forecast shows up to a ${Math.round(maxSpread)}°C difference between daily highs and lows. Pack breathable base layers and a jacket for evenings.`,
      });
    }
  }

  // 3. Apparent temperature / wind chill
  if (current?.temperature != null && current?.apparent_temperature != null) {
    const diff = current.apparent_temperature - current.temperature;
    if (diff <= -3) {
      considerations.push({
        category: "Comfort",
        title: "Wind chill effect",
        detail: `Feels around ${Math.abs(Math.round(diff))}°C cooler than the ambient thermometer reading due to wind and humidity.`,
      });
    } else if (diff >= 3) {
      considerations.push({
        category: "Comfort",
        title: "Higher heat index",
        detail: `Feels around ${Math.round(diff)}°C warmer than measured due to humidity. Stay hydrated during outdoor exploration.`,
      });
    }
  }

  // 4. Air quality caution
  if (airQuality?.us_aqi && airQuality.us_aqi > 50) {
    considerations.push({
      category: "Health & Well-being",
      title: `Elevated AQI (${airQuality.us_aqi})`,
      detail: "Sensitive travelers with allergies or asthma should consider limiting prolonged outdoor exertion.",
    });
  }

  // 5. Sun & UV / Clear skies
  if (current?.cloud_cover != null && current.cloud_cover <= 15 && current?.is_day !== 0) {
    considerations.push({
      category: "Sun Exposure",
      title: "Clear sky exposure",
      detail: "Very low cloud cover during daylight hours. Bring sunglasses and apply sun protection if spending extended time outside.",
    });
  }

  if (considerations.length === 0) {
    considerations.push({
      category: "General",
      title: "Mild & stable conditions",
      detail: "Weather conditions are moderate with no major alerts. Standard travel attire is suitable.",
    });
  }

  return (
    <section className="panel" aria-labelledby="traveler-heading">
      <div className="panel-header">
        <h2 id="traveler-heading">Traveler Considerations &amp; Insights</h2>
        <span className="hint">Non-obvious considerations for your trip</span>
      </div>
      <div className="stats" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(16rem, 1fr))" }}>
        {considerations.map((item, idx) => (
          <div key={idx} className="stat" style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
            <span style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--primary)", fontWeight: 700 }}>
              {item.category}
            </span>
            <strong style={{ fontSize: "0.95rem" }}>{item.title}</strong>
            <p style={{ margin: 0, fontSize: "0.85rem", color: "var(--muted)", lineHeight: 1.4 }}>{item.detail}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

