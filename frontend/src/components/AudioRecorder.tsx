/**
 * AudioRecorder component with Listen button.
 *
 * Handles microphone access, recording, upload, and processing coordination.
 */

import { useState, useRef, useEffect } from 'react';
import { api } from '../services/api';
import type { ProcessingStatus, SummaryResponse } from '../types';
import { ProcessingIndicator } from './ProcessingIndicator';
import { SummaryDisplay } from './SummaryDisplay';

export function AudioRecorder() {
  const [status, setStatus] = useState<ProcessingStatus>('idle');
  const [recordingTime, setRecordingTime] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [audioId, setAudioId] = useState<string>('');

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<number | null>(null);
  const pollingRef = useRef<number | null>(null);

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (pollingRef.current) clearInterval(pollingRef.current);
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        mediaRecorderRef.current.stop();
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm',
      });

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      // Handle data available
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      // Handle recording stopped
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await uploadAudio(audioBlob);

        // Stop all tracks
        stream.getTracks().forEach((track) => track.stop());
      };

      // Start recording
      mediaRecorder.start();
      setStatus('recording');
      setRecordingTime(0);
      setErrorMessage('');

      // Start timer
      timerRef.current = window.setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      setErrorMessage('Failed to access microphone. Please grant permission.');
      setStatus('error');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  const uploadAudio = async (audioBlob: Blob) => {
    setStatus('uploading');

    try {
      // Create file from blob
      const file = new File([audioBlob], `recording_${Date.now()}.webm`, {
        type: 'audio/webm',
      });

      // Upload to backend
      const uploadResponse = await api.uploadAudio(file);
      setAudioId(uploadResponse.id);

      // Start processing
      await api.startProcessing(uploadResponse.id);
      setStatus('processing');

      // Start polling for status
      startStatusPolling(uploadResponse.id);
    } catch (error: any) {
      console.error('Upload failed:', error);
      setErrorMessage(error.response?.data?.detail || 'Failed to upload audio');
      setStatus('error');
    }
  };

  const startStatusPolling = (audioId: string) => {
    pollingRef.current = window.setInterval(async () => {
      try {
        const statusResponse = await api.getAudioStatus(audioId);

        if (statusResponse.status === 'completed' && statusResponse.summary_id) {
          // Fetch summary
          const summaryResponse = await api.getSummary(statusResponse.summary_id);
          setSummary(summaryResponse);
          setStatus('completed');

          // Stop polling
          if (pollingRef.current) {
            clearInterval(pollingRef.current);
            pollingRef.current = null;
          }
        } else if (statusResponse.status === 'failed') {
          setErrorMessage(statusResponse.error_message || 'Processing failed');
          setStatus('error');

          // Stop polling
          if (pollingRef.current) {
            clearInterval(pollingRef.current);
            pollingRef.current = null;
          }
        }
      } catch (error) {
        console.error('Status polling error:', error);
      }
    }, 2000); // Poll every 2 seconds
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const reset = () => {
    setStatus('idle');
    setRecordingTime(0);
    setErrorMessage('');
    setSummary(null);
    setAudioId('');
  };

  return (
    <div className="audio-recorder">
      <h1>Meeting Notes Summarizer</h1>

      {errorMessage && (
        <div className="error-message">
          <p>{errorMessage}</p>
          <button onClick={reset}>Try Again</button>
        </div>
      )}

      {status === 'idle' && (
        <div className="listen-container">
          <button className="listen-button" onClick={startRecording}>
            <span className="mic-icon">🎤</span>
            Listen
          </button>
          <p>Click to start recording your meeting</p>
        </div>
      )}

      {status === 'recording' && (
        <div className="recording-container">
          <button className="stop-button" onClick={stopRecording}>
            <span className="stop-icon">⏹</span>
            Stop Recording
          </button>
          <div className="recording-indicator">
            <span className="pulse-dot"></span>
            <span className="recording-time">{formatTime(recordingTime)}</span>
          </div>
        </div>
      )}

      {(status === 'uploading' || status === 'processing') && (
        <ProcessingIndicator status={status} />
      )}

      {status === 'completed' && summary && (
        <div className="results-container">
          <SummaryDisplay summary={summary} />
          <button className="new-recording-button" onClick={reset}>
            New Recording
          </button>
        </div>
      )}
    </div>
  );
}
