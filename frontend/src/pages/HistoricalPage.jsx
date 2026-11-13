import { useState } from "react";
import DateRangeFields from "../components/DateRangeFields.jsx";
import LocationSearch from "../components/LocationSearch.jsx";
import LocationSummary from "../components/LocationSummary.jsx";
import { ErrorMessage, InfoMessage, SuccessMessage } from "../components/Messages.jsx";
import ObservationsTable from "../components/ObservationsTable.jsx";
import { createRecord, getHistorical } from "../services/api.js";
import { validateDateRange } from "../utils/dates.js";
import { buildRecordPayload } from "../utils/records.js";

const IDLE_LOOKUP = { loading: false, error: "", result: null };
const IDLE_SAVE = { saving: false, error: "", savedId: null };

export default function HistoricalPage({ location, onSelectLocation, onOpenRecord }) {
  const [dates, setDates] = useState({ start: "", end: "" });
  const [validationError, setValidationError] = useState("");
  const [lookup, setLookup] = useState(IDLE_LOOKUP);
  const [save, setSave] = useState(IDLE_SAVE);

  async function handleSubmit(event) {
    event.preventDefault();
    const problem = validateDateRange(dates.start, dates.end);
    setValidationError(problem ?? "");
    if (problem) return;
    setSave(IDLE_SAVE);
    setLookup({ loading: true, error: "", result: null });
    try {
      const history = await getHistorical(location, dates.start, dates.end);
      // keep the exact request so saving matches what is displayed
      setLookup({ loading: false, error: "", result: { ...history, location, start: dates.start, end: dates.end } });
    } catch (error) {
      setLookup({ loading: false, error: error.message, result: null });
    }
  }

  async function handleSave() {
    const { location: searched, start, end } = lookup.result;
    setSave({ saving: true, error: "", savedId: null });
    try {
      const record = await createRecord(buildRecordPayload(searched, start, end));
      setSave({ saving: false, error: "", savedId: record.id });
    } catch (error) {
      setSave({ saving: false, error: error.message, savedId: null });
    }
  }

  const result = lookup.result;
  return (
    <>
      <LocationSearch selectedLocation={location} onSelect={onSelectLocation} />
      <section className="panel" aria-labelledby="historical-heading">
        <h2 id="historical-heading">Historical weather</h2>
        {!location ? (
          <InfoMessage>Select a location above before searching historical weather.</InfoMessage>
        ) : (
          <>
            <LocationSummary location={location} />
            <form onSubmit={handleSubmit} noValidate>
              <DateRangeFields start={dates.start} end={dates.end} onChange={setDates} disabled={lookup.loading} />
              {validationError && <ErrorMessage message={validationError} />}
              <button type="submit" disabled={lookup.loading || save.saving}>
                {lookup.loading ? "Searching…" : "Search historical weather"}
              </button>
            </form>
          </>
        )}
        {lookup.loading && <p role="status">Loading historical weather…</p>}
        {lookup.error && <ErrorMessage message={lookup.error} />}
      </section>

      {result && (
        <section className="panel" aria-labelledby="results-heading">
          <div className="panel-header">
            <h2 id="results-heading">
              {result.start} to {result.end}
            </h2>
            <button type="button" onClick={handleSave} disabled={save.saving || save.savedId !== null}>
              {save.saving ? "Saving…" : "Save record"}
            </button>
          </div>
          {save.error && <ErrorMessage message={save.error} />}
          {save.savedId !== null && (
            <SuccessMessage>
              Record saved.{" "}
              <button type="button" className="link-button" onClick={() => onOpenRecord(save.savedId)}>
                View saved record
              </button>
            </SuccessMessage>
          )}
          <ObservationsTable observations={result.days} dataset={result.dataset} />
        </section>
      )}
    </>
  );
}
