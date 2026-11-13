import { useState } from "react";
import useRequest from "../hooks/useRequest.js";
import { getRecord, updateRecord } from "../services/api.js";
import { validateDateRange } from "../utils/dates.js";
import { buildRecordPayload, locationFromRecord } from "../utils/records.js";
import AsyncContent from "./AsyncContent.jsx";
import DateRangeFields from "./DateRangeFields.jsx";
import LocationSearch from "./LocationSearch.jsx";
import LocationSummary from "./LocationSummary.jsx";
import { ErrorMessage } from "./Messages.jsx";

function EditForm({ record, onCancel, onSaved }) {
  const [location, setLocation] = useState(locationFromRecord(record));
  const [dates, setDates] = useState({ start: record.start_date, end: record.end_date });
  const [validationError, setValidationError] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    const problem = validateDateRange(dates.start, dates.end);
    setValidationError(problem ?? "");
    setError("");
    if (problem) return;
    setSaving(true);
    try {
      await updateRecord(record.id, buildRecordPayload(location, dates.start, dates.end));
      onSaved();
    } catch (requestError) {
      setError(requestError.message);
      setSaving(false);
    }
  }

  return (
    <>
      <LocationSearch selectedLocation={location} onSelect={setLocation} />
      <section className="panel" aria-labelledby="edit-heading">
        <h2 id="edit-heading">Edit record</h2>
        <LocationSummary location={location} />
        <form onSubmit={handleSubmit}>
          <DateRangeFields start={dates.start} end={dates.end} onChange={setDates} disabled={saving} />
          {validationError && <ErrorMessage message={validationError} />}
          <p className="note">
            Saving fetches fresh historical data for these settings. If the provider request fails, the existing record is
            kept unchanged.
          </p>
          {error && <ErrorMessage message={error} />}
          <div className="row">
            <button type="submit" disabled={saving}>
              {saving ? "Saving…" : "Save changes"}
            </button>
            <button type="button" className="button-secondary" onClick={onCancel} disabled={saving}>
              Cancel
            </button>
          </div>
        </form>
      </section>
    </>
  );
}

export default function RecordEditForm({ recordId, onCancel, onSaved }) {
  const request = useRequest(() => getRecord(recordId), [recordId]);
  return (
    <AsyncContent request={request} loadingText="Loading record…">
      {(record) => <EditForm record={record} onCancel={onCancel} onSaved={onSaved} />}
    </AsyncContent>
  );
}
