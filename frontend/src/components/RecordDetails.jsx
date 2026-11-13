import useRequest from "../hooks/useRequest.js";
import { getRecord } from "../services/api.js";
import { formatDateTime } from "../utils/format.js";
import AsyncContent from "./AsyncContent.jsx";
import MapLink from "./MapLink.jsx";
import ObservationsTable from "./ObservationsTable.jsx";

export default function RecordDetails({ recordId, onBack, onEdit }) {
  const request = useRequest(() => getRecord(recordId), [recordId]);
  return (
    <section className="panel" aria-labelledby="record-heading">
      <div className="panel-header">
        <h2 id="record-heading">Record details</h2>
        <div className="row">
          <button type="button" className="button-secondary" onClick={onBack}>
            Back to saved records
          </button>
          {request.data && (
            <button type="button" onClick={() => onEdit(recordId)}>
              Edit
            </button>
          )}
        </div>
      </div>
      <AsyncContent request={request} loadingText="Loading record…">
        {(record) => (
          <>
            <dl className="details">
              <div>
                <dt>Location</dt>
                <dd>{record.location_name}</dd>
              </div>
              <div>
                <dt>Region / country</dt>
                <dd>{[record.admin_area, record.country].filter(Boolean).join(", ") || "—"}</dd>
              </div>
              <div>
                <dt>Coordinates</dt>
                <dd>
                  {record.latitude}, {record.longitude} · <MapLink location={record} />
                </dd>
              </div>
              <div>
                <dt>Date range</dt>
                <dd>
                  {record.start_date} to {record.end_date}
                </dd>
              </div>
              <div>
                <dt>Time zone</dt>
                <dd>{record.timezone ?? "—"}</dd>
              </div>
              <div>
                <dt>Source</dt>
                <dd>
                  {record.provider} · {record.dataset}
                </dd>
              </div>
              <div>
                <dt>Saved</dt>
                <dd>{formatDateTime(record.created_at)}</dd>
              </div>
              <div>
                <dt>Last updated</dt>
                <dd>{formatDateTime(record.updated_at)}</dd>
              </div>
            </dl>
            <ObservationsTable observations={record.observations} dataset={record.dataset} />
          </>
        )}
      </AsyncContent>
    </section>
  );
}
