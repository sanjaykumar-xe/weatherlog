const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(message, { code = "unknown", status = 0 } = {}) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

async function toApiError(response) {
  try {
    const body = await response.json();
    if (body?.error?.message) {
      return new ApiError(body.error.message, { code: body.error.code, status: response.status });
    }
  } catch {
    // fall through to the generic message
  }
  return new ApiError(`The server returned an unexpected error (${response.status}).`, { status: response.status });
}

async function request(path, options) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, options);
  } catch {
    throw new ApiError("Cannot reach the WeatherLog server. Check that the backend is running and try again.", {
      code: "network_error",
    });
  }
  if (!response.ok) throw await toApiError(response);
  return response;
}

async function requestJson(path, options) {
  const response = await request(path, options);
  return response.json();
}

const query = (params) => new URLSearchParams(params).toString();
const coordinates = ({ latitude, longitude }) => query({ latitude, longitude });
const jsonRequest = (method, payload) => ({
  method,
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload),
});

export const searchLocations = async (text) => (await requestJson(`/locations/search?${query({ q: text })}`)).data;

export const getCurrentWeather = async (location) =>
  (await requestJson(`/weather/current?${coordinates(location)}`)).data;

export const getForecast = async (location) => (await requestJson(`/weather/forecast?${coordinates(location)}`)).data;

export const getAirQuality = async (location) =>
  (await requestJson(`/weather/air-quality?${coordinates(location)}`)).data;

export const getHistorical = async (location, startDate, endDate) =>
  (
    await requestJson(
      `/weather/historical?${query({
        latitude: location.latitude,
        longitude: location.longitude,
        start_date: startDate,
        end_date: endDate,
      })}`
    )
  ).data;

export async function listRecords({ limit = 50, offset = 0 } = {}) {
  const body = await requestJson(`/records?${query({ limit, offset })}`);
  return { records: body.data, total: body.meta.total };
}

export const getRecord = async (id) => (await requestJson(`/records/${id}`)).data;
export const createRecord = async (payload) => (await requestJson("/records", jsonRequest("POST", payload))).data;
export const updateRecord = async (id, payload) =>
  (await requestJson(`/records/${id}`, jsonRequest("PUT", payload))).data;
export const deleteRecord = async (id) => (await requestJson(`/records/${id}`, { method: "DELETE" })).data;

export async function downloadExport(format) {
  const response = await request(`/records/export?${query({ format })}`);
  const url = URL.createObjectURL(await response.blob());
  const link = document.createElement("a");
  link.href = url;
  link.download = `weatherlog-records.${format}`;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
