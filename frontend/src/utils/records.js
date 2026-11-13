export function buildRecordPayload(location, startDate, endDate) {
  return {
    location_name: location.name,
    admin_area: location.admin_area ?? null,
    country: location.country ?? null,
    latitude: location.latitude,
    longitude: location.longitude,
    start_date: startDate,
    end_date: endDate,
  };
}

export function locationFromRecord(record) {
  return {
    name: record.location_name,
    admin_area: record.admin_area,
    country: record.country,
    latitude: record.latitude,
    longitude: record.longitude,
  };
}
