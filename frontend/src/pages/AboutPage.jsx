export default function AboutPage() {
  const applicantName = import.meta.env.VITE_APPLICANT_NAME || "Sanjay Kumar";

  return (
    <div className="panel about-panel">
      <div className="panel-header">
        <h2>About PM Accelerator & Project</h2>
      </div>

      <section style={{ marginBottom: "1.5rem" }}>
        <h3>Product Manager Accelerator</h3>
        <p>
          <strong>Product Manager Accelerator</strong> is a premier global learning community and career accelerator
          designed to empower aspiring and experienced professionals to break into and excel in Product Management,
          AI, and Technology roles.
        </p>
        <p>
          Through hands-on mentorship, end-to-end industry training, and real-world product development experience,
          PM Accelerator bridges the gap between academic theory and high-impact industry execution.
        </p>
        <p>
          <a
            href="https://www.linkedin.com/company/product-manager-accelerator/"
            target="_blank"
            rel="noopener noreferrer"
          >
            Visit PM Accelerator on LinkedIn &rarr;
          </a>
        </p>
      </section>

      <section style={{ marginBottom: "1.5rem" }}>
        <h3>Applicant Details</h3>
        <ul style={{ listStyle: "none", padding: 0, margin: "0.5rem 0" }}>
          <li><strong>Applicant:</strong> {applicantName}</li>
          <li><strong>Target Role:</strong> AI Engineer Intern (AI / ML / GenAI Application)</li>
          <li><strong>Assessment:</strong> Full Stack Submission (Tech Assessment #1 &amp; #2)</li>
        </ul>
      </section>

      <section>
        <h3>System Implementation Overview</h3>
        <div className="details" style={{ margin: "0.5rem 0" }}>
          <div>
            <dt>Tech Assessment #1 (Frontend)</dt>
            <dd>React 18 SPA (Vite), responsive layouts (desktop, tablet, mobile), geolocation, 5-day forecast, air quality metrics, and resilient error recovery.</dd>
          </div>
          <div>
            <dt>Tech Assessment #2 (Backend)</dt>
            <dd>FastAPI REST service, SQLite + SQLModel ORM, full CRUD on historical lookups, input validation, and CSV / JSON exports.</dd>
          </div>
        </div>
      </section>
    </div>
  );
}

