import { useState } from "react";
import AboutPage from "./pages/AboutPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import HistoricalPage from "./pages/HistoricalPage.jsx";
import SavedPage from "./pages/SavedPage.jsx";

const PAGES = [
  { id: "dashboard", label: "Dashboard" },
  { id: "historical", label: "Historical search" },
  { id: "saved", label: "Saved records" },
  { id: "about", label: "About PM Accelerator" },
];

const applicantName = import.meta.env.VITE_APPLICANT_NAME || "Sanjay Kumar";

export default function App() {
  const [page, setPage] = useState("dashboard");
  const [location, setLocation] = useState(null);
  const [recordToOpen, setRecordToOpen] = useState(null);

  function navigate(nextPage, recordId = null) {
    setRecordToOpen(recordId);
    setPage(nextPage);
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>WeatherLog</h1>
        <nav aria-label="Main">
          {PAGES.map(({ id, label }) => (
            <button
              key={id}
              type="button"
              className="nav-button"
              aria-current={page === id ? "page" : undefined}
              onClick={() => navigate(id)}
            >
              {label}
            </button>
          ))}
        </nav>
      </header>
      <main>
        {page === "dashboard" && <DashboardPage location={location} onSelectLocation={setLocation} />}
        {page === "historical" && (
          <HistoricalPage
            location={location}
            onSelectLocation={setLocation}
            onOpenRecord={(id) => navigate("saved", id)}
          />
        )}
        {page === "saved" && <SavedPage initialRecordId={recordToOpen} />}
        {page === "about" && <AboutPage />}
      </main>
      <footer className="app-footer">
        <p>
          Weather, air-quality and geocoding data by{" "}
          <a href="https://open-meteo.com/" target="_blank" rel="noopener noreferrer">
            Open-Meteo.com
          </a>{" "}
          (CC BY 4.0).
        </p>
        <p>Built by {applicantName} for the Product Manager Accelerator (PM Accelerator) Technical Assessment.</p>
      </footer>
    </div>
  );
}
