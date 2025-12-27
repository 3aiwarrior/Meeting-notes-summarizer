// API Response Types

export interface AudioUploadResponse {
  id: string;
  filename: string;
  file_size: number;
  status: string;
  created_at: string;
}

export interface AudioStatusResponse {
  id: string;
  filename: string;
  status: string;
  duration_seconds?: number;
  error_message?: string;
  transcription_id?: string;
  summary_id?: string;
  created_at: string;
  updated_at: string;
}

export interface SummaryResponse {
  id: string;
  transcription_id: string;
  summary_text: string;
  key_points: string[];
  action_items: { item: string; owner: string }[];
  decisions: string[];
  participants: string[];
  tokens_used?: number;
  model_used?: string;
  status: string;
  created_at: string;
}

export interface TranscriptionResponse {
  id: string;
  audio_file_id: string;
  full_text: string;
  language?: string;
  status: string;
  processing_time_ms?: number;
  created_at: string;
}

export type ProcessingStatus = 'idle' | 'recording' | 'uploading' | 'processing' | 'completed' | 'error';
