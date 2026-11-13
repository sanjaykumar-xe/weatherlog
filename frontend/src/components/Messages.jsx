export function ErrorMessage({ message, onRetry }) {
  return (
    <div className="message message-error" role="alert">
      <p>
        <strong>Error:</strong> {message}
      </p>
      {onRetry && (
        <button type="button" className="button-secondary" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  );
}

export function InfoMessage({ children }) {
  return (
    <div className="message message-info" role="status">
      {children}
    </div>
  );
}

export function SuccessMessage({ children }) {
  return (
    <div className="message message-success" role="status">
      <strong>Success:</strong> {children}
    </div>
  );
}
