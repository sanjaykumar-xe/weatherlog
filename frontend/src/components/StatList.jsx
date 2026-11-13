export default function StatList({ items }) {
  return (
    <dl className="stats">
      {items.map(({ label, value }) => (
        <div key={label} className="stat">
          <dt>{label}</dt>
          <dd>{value}</dd>
        </div>
      ))}
    </dl>
  );
}
