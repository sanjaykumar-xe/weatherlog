import { useState } from "react";
import { SuccessMessage } from "../components/Messages.jsx";
import RecordDetails from "../components/RecordDetails.jsx";
import RecordEditForm from "../components/RecordEditForm.jsx";
import RecordList from "../components/RecordList.jsx";

export default function SavedPage({ initialRecordId }) {
  const [view, setView] = useState(initialRecordId ? { mode: "detail", id: initialRecordId } : { mode: "list" });
  const [notice, setNotice] = useState("");

  const show = (nextView) => {
    setNotice("");
    setView(nextView);
  };

  return (
    <>
      {notice && <SuccessMessage>{notice}</SuccessMessage>}
      {view.mode === "list" && (
        <RecordList
          onView={(id) => show({ mode: "detail", id })}
          onEdit={(id) => show({ mode: "edit", id })}
          onNotice={setNotice}
        />
      )}
      {view.mode === "detail" && (
        <RecordDetails
          recordId={view.id}
          onBack={() => show({ mode: "list" })}
          onEdit={(id) => show({ mode: "edit", id })}
        />
      )}
      {view.mode === "edit" && (
        <RecordEditForm
          recordId={view.id}
          onCancel={() => show({ mode: "detail", id: view.id })}
          onSaved={() => {
            setView({ mode: "detail", id: view.id });
            setNotice("Record updated with fresh data.");
          }}
        />
      )}
    </>
  );
}
