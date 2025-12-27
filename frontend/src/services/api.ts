/**
 * API service for backend communication.
 */

import axios from 'axios';
import type {
  AudioUploadResponse,
  AudioStatusResponse,
  SummaryResponse,
  TranscriptionResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  /**
   * Upload audio file to backend.
   */
  async uploadAudio(file: File): Promise<AudioUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<AudioUploadResponse>('/api/v1/audio/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  /**
   * Get audio file status.
   */
  async getAudioStatus(audioId: string): Promise<AudioStatusResponse> {
    const response = await apiClient.get<AudioStatusResponse>(`/api/v1/audio/${audioId}`);
    return response.data;
  },

  /**
   * Start processing audio file (transcription + summarization).
   */
  async startProcessing(audioId: string): Promise<{ message: string; audio_id: string; status: string }> {
    const response = await apiClient.post(`/api/v1/process/${audioId}`);
    return response.data;
  },

  /**
   * Get transcription by ID.
   */
  async getTranscription(transcriptionId: string): Promise<TranscriptionResponse> {
    const response = await apiClient.get<TranscriptionResponse>(`/api/v1/transcription/${transcriptionId}`);
    return response.data;
  },

  /**
   * Get summary by ID.
   */
  async getSummary(summaryId: string): Promise<SummaryResponse> {
    const response = await apiClient.get<SummaryResponse>(`/api/v1/summary/${summaryId}`);
    return response.data;
  },

  /**
   * Health check.
   */
  async healthCheck(): Promise<{ status: string; version: string; database: string }> {
    const response = await apiClient.get('/api/v1/health');
    return response.data;
  },
};
