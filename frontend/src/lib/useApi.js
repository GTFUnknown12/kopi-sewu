import { useEffect, useState } from 'react';
import { api } from './api.js';

export function useApi(path) {
  const [state, setState] = useState({ data: null, error: '', loading: true });
  useEffect(() => {
    let alive = true;
    api(path)
      .then((data) => alive && setState({ data, error: '', loading: false }))
      .catch((e) => alive && setState({ data: null, error: e.message, loading: false }));
    return () => { alive = false; };
  }, [path]);
  return state;
}
