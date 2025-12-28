/**
 * useAudioUpload hook for handling audio file uploads.
 */

import { useState, useCallback } from 'react';
import { api } from '../services/api';
import type { AudioUploadResponse, ProcessingStatus } from '../types';

interface UseAudioUploadReturn {
  upload: (file: File) => Promise<AudioUploadResponse | null>;
  status: ProcessingStatus;
  error: string | null;
  reset: () => void;
}

export function useAudioUpload(): UseAudioUploadReturn {
  const [status, setStatus] = useState<ProcessingStatus>('idle');
  const [error, setError] = useState<string | null>(null);

  const upload = useCallback(async (file: File): Promise<AudioUploadResponse | null> => {
    setStatus('uploading');
    setError(null);

    try {
      const response = await api.uploadAudio(file);
      setStatus('idle');
      return response;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Upload failed';
      setError(errorMessage);
      setStatus('error');
      return null;
    }
  }, []);

  const reset = useCallback(() => {
    setStatus('idle');
    setError(null);
  }, []);

  return { upload, status, error, reset };
}
