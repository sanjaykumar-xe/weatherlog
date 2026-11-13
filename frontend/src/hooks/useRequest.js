import { useEffect, useState } from "react";

// Runs `loader` whenever `deps` change. Pass a null loader to stay idle.
export default function useRequest(loader, deps) {
  const [state, setState] = useState({ data: null, error: null, loading: false });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    if (!loader) {
      setState({ data: null, error: null, loading: false });
      return undefined;
    }
    let cancelled = false;
    setState({ data: null, error: null, loading: true });
    loader()
      .then((data) => !cancelled && setState({ data, error: null, loading: false }))
      .catch((error) => !cancelled && setState({ data: null, error, loading: false }));
    return () => {
      cancelled = true;
    };
  }, [...deps, attempt]);

  return { ...state, retry: () => setAttempt((count) => count + 1) };
}
