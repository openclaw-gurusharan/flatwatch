'use client';

import { useEffect, useState } from 'react';
import { fetchTrustSnapshot, type TrustSnapshot } from './trust';

const DEFAULT_SNAPSHOT: TrustSnapshot = {
  state: 'no_identity',
  eligible: false,
  reason: null,
  trust: null,
};

export function useTrustState(subjectId?: string | null) {
  const [snapshot, setSnapshot] = useState<TrustSnapshot>(DEFAULT_SNAPSHOT);
  const [loading, setLoading] = useState(Boolean(subjectId));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!subjectId) {
      setSnapshot(DEFAULT_SNAPSHOT);
      setLoading(false);
      setError(null);
      return;
    }

    let cancelled = false;

    const run = async () => {
      try {
        setLoading(true);
        setError(null);
        const next = await fetchTrustSnapshot(subjectId);
        if (!cancelled) {
          setSnapshot(next);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load trust state.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    void run();

    return () => {
      cancelled = true;
    };
  }, [subjectId]);

  return {
    ...snapshot,
    loading,
    error,
  };
}
