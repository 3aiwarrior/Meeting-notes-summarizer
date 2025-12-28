/**
 * usePolling hook for polling API status.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { api } from '../services/api';
import type { AudioStatusResponse, SummaryResponse } from '../types';

interface UsePollingOptions {
  audioId: string | null;
  interval?: number;
  enabled?: boolean;
}

interface UsePollingReturn {
  audioStatus: AudioStatusResponse | null;
  summary: SummaryResponse | null;
  isPolling: boolean;
  error: string | null;
  startPolling: () => void;
  stopPolling: () => void;
}

export function usePolling({
  audioId,
  interval = 2000,
  enabled = true,
}: UsePollingOptions): UsePollingReturn {
  const [audioStatus, setAudioStatus] = useState<AudioStatusResponse | null>(null);
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pollingRef = useRef<number | null>(null);

  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
    setIsPolling(false);
  }, []);

  const poll = useCallback(async () => {
    if (!audioId) return;

    try {
      const status = await api.getAudioStatus(audioId);
      setAudioStatus(status);

      if (status.status === 'completed' && status.summary_id) {
        const summaryData = await api.getSummary(status.summary_id);
        setSummary(summaryData);
        stopPolling();
      } else if (status.status === 'failed') {
        setError(status.error_message || 'Processing failed');
        stopPolling();
      }
    } catch (err: any) {
      setError(err.message || 'Polling failed');
      stopPolling();
    }
  }, [audioId, stopPolling]);

  const startPolling = useCallback(() => {
    if (!audioId || pollingRef.current) return;

    setIsPolling(true);
    setError(null);

    // Initial poll
    poll();

    // Set up interval
    pollingRef.current = window.setInterval(poll, interval);
  }, [audioId, interval, poll]);

  useEffect(() => {
    if (enabled && audioId) {
      startPolling();
    }

    return () => {
      stopPolling();
    };
  }, [enabled, audioId, startPolling, stopPolling]);

  return {
    audioStatus,
    summary,
    isPolling,
    error,
    startPolling,
    stopPolling,
  };
}
