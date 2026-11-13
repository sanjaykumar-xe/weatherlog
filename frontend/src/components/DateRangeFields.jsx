import { useId } from "react";
import { EARLIEST_DATE, MAX_RANGE_DAYS, todayIso } from "../utils/dates.js";

export default function DateRangeFields({ start, end, onChange, disabled }) {
  const id = useId();
  return (
    <fieldset className="date-range" disabled={disabled}>
      <legend>Date range (up to {MAX_RANGE_DAYS} days)</legend>
      <div>
        <label htmlFor={`${id}-start`}>Start date</label>
        <input
          id={`${id}-start`}
          type="date"
          value={start}
          min={EARLIEST_DATE}
          max={todayIso()}
          onChange={(event) => onChange({ start: event.target.value, end })}
        />
      </div>
      <div>
        <label htmlFor={`${id}-end`}>End date</label>
        <input
          id={`${id}-end`}
          type="date"
          value={end}
          min={EARLIEST_DATE}
          max={todayIso()}
          onChange={(event) => onChange({ start, end: event.target.value })}
        />
      </div>
    </fieldset>
  );
}
