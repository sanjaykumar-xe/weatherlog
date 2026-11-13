import { ErrorMessage } from "./Messages.jsx";

// renders the loading, error or loaded state of a useRequest result
export default function AsyncContent({ request, loadingText, children }) {
  if (request.loading) return <p role="status">{loadingText}</p>;
  if (request.error) return <ErrorMessage message={request.error.message} onRetry={request.retry} />;
  if (!request.data) return null;
  return children(request.data);
}
