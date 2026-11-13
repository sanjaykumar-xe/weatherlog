import { useState } from "react";
import useRequest from "../hooks/useRequest.js";
import { deleteRecord, downloadExport, listRecords } from "../services/api.js";
import { formatDateTime } from "../utils/format.js";
import AsyncContent from "./AsyncContent.jsx";
import { ErrorMessage, InfoMessage } from "./Messages.jsx";

export default function RecordList({ onView, onEdit, onNotice }) {
  const request = useRequest(() => listRecords(), []);
  const [busyId, setBusyId] = useState(null);
  const [exportingFormat, setExportingFormat] = useState("");
  const [actionError, setActionError] = useState("");
  const busy = busyId !== null || exportingFormat !== "";
  const isEmpty = request.data?.records.length === 0;

  async function handleDelete(record) {
    const label = `${record.location_name} (${record.start_date} to ${record.end_date})`;
    if (!window.confirm(`Delete the saved record for ${label}? This cannot be undone.`)) return;
    setBusyId(record.id);
    setActionError("");
    try {
      await deleteRecord(record.id);
      onNotice("Record deleted.");
      request.retry();
    } catch (error) {
      setActionError(error.message);
    } finally {
      setBusyId(null);
    }
  }

  async function handleExport(format) {
    setExportingFormat(format);
    setActionError("");
    try {
      await downloadExport(format);
    } catch (error) {
      setActionError(error.message);
    } finally {
      setExportingFormat("");
    }
  }

  return (
    <section className="panel" aria-labelledby="saved-heading">
      <div className="panel-header">
        <h2 id="saved-heading">Saved records</h2>
        <div className="row">
          {["csv", "json"].map((format) => (
            <button
              key={format}
              type="button"
              className="button-secondary"
              disabled={busy || request.loading || isEmpty}
              onClick={() => handleExport(format)}
            >
              {exportingFormat === format ? "Exporting…" : `Export ${format.toUpperCase()}`}
            </button>
          ))}
        </div>
      </div>
      {actionError && <ErrorMessage message={actionError} />}
      <AsyncContent request={request} loadingText="Loading saved records…">
        {({ records, total }) =>
          records.length === 0 ? (
            <InfoMessage>
              No records saved yet. Run a historical search and choose “Save record” to keep it here.
            </InfoMessage>
          ) : (
            <>
              {total > records.length && (
                <p className="note">
                  Showing the latest {records.length} of {total} records. Exports include all {total}.
                </p>
              )}
              <ul className="record-list">
                {records.map((record) => (
                  <li key={record.id} className="record-item">
                    <div>
                      <h3>{record.location_name}</h3>
                      <p>
                        {record.start_date} to {record.end_date} · {record.observation_count} daily{" "}
                        {record.observation_count === 1 ? "observation" : "observations"}
                      </p>
                      <p className="hint">Saved {formatDateTime(record.created_at)}</p>
                    </div>
                    <div className="row">
                      <button type="button" className="button-secondary" disabled={busy} onClick={() => onView(record.id)}>
                        View
                        <span className="sr-only"> {record.location_name}</span>
                      </button>
                      <button type="button" className="button-secondary" disabled={busy} onClick={() => onEdit(record.id)}>
                        Edit
                        <span className="sr-only"> {record.location_name}</span>
                      </button>
                      <button type="button" className="button-danger" disabled={busy} onClick={() => handleDelete(record)}>
                        {busyId === record.id ? "Deleting…" : "Delete"}
                        <span className="sr-only"> {record.location_name}</span>
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            </>
          )
        }
      </AsyncContent>
    </section>
  );
}
