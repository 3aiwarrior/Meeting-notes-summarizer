/**
 * ResultsPage component - Display meeting summary results.
 */

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { SummaryDisplay } from '../components/SummaryDisplay';
import { ProcessingIndicator } from '../components/ProcessingIndicator';
import { Button } from '../components/ui';
import type { SummaryResponse, AudioStatusResponse } from '../types';

export function ResultsPage() {
  const { audioId } = useParams<{ audioId: string }>();
  const navigate = useNavigate();
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [status, setStatus] = useState<string>('loading');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (!audioId) {
      navigate('/upload');
      return;
    }

    const fetchResults = async () => {
      try {
        const audioStatus: AudioStatusResponse = await api.getAudioStatus(audioId);

        if (audioStatus.status === 'completed' && audioStatus.summary_id) {
          const summaryData = await api.getSummary(audioStatus.summary_id);
          setSummary(summaryData);
          setStatus('completed');
        } else if (audioStatus.status === 'failed') {
          setError(audioStatus.error_message || 'Processing failed');
          setStatus('error');
        } else {
          setStatus('processing');
          // Poll for status
          const interval = setInterval(async () => {
            const updatedStatus = await api.getAudioStatus(audioId);
            if (updatedStatus.status === 'completed' && updatedStatus.summary_id) {
              const summaryData = await api.getSummary(updatedStatus.summary_id);
              setSummary(summaryData);
              setStatus('completed');
              clearInterval(interval);
            } else if (updatedStatus.status === 'failed') {
              setError(updatedStatus.error_message || 'Processing failed');
              setStatus('error');
              clearInterval(interval);
            }
          }, 2000);

          return () => clearInterval(interval);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to fetch results');
        setStatus('error');
      }
    };

    fetchResults();
  }, [audioId, navigate]);

  if (status === 'loading' || status === 'processing') {
    return (
      <div className="results-page">
        <ProcessingIndicator status="processing" />
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="results-page">
        <div className="error-container">
          <h2>Error</h2>
          <p>{error}</p>
          <Button onClick={() => navigate('/upload')}>Try Again</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="results-page">
      {summary && <SummaryDisplay summary={summary} />}
      <Button onClick={() => navigate('/upload')} className="new-recording-btn">
        New Recording
      </Button>
    </div>
  );
}
