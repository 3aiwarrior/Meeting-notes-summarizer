/**
 * MeetingContext for global state management.
 */

import { createContext, useContext, useState, ReactNode } from 'react';
import type { SummaryResponse, AudioStatusResponse, ProcessingStatus } from '../types';

interface MeetingState {
  currentAudioId: string | null;
  status: ProcessingStatus;
  audioStatus: AudioStatusResponse | null;
  summary: SummaryResponse | null;
  error: string | null;
}

interface MeetingContextValue extends MeetingState {
  setCurrentAudioId: (id: string | null) => void;
  setStatus: (status: ProcessingStatus) => void;
  setAudioStatus: (status: AudioStatusResponse | null) => void;
  setSummary: (summary: SummaryResponse | null) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState: MeetingState = {
  currentAudioId: null,
  status: 'idle',
  audioStatus: null,
  summary: null,
  error: null,
};

const MeetingContext = createContext<MeetingContextValue | undefined>(undefined);

interface MeetingProviderProps {
  children: ReactNode;
}

export function MeetingProvider({ children }: MeetingProviderProps) {
  const [state, setState] = useState<MeetingState>(initialState);

  const setCurrentAudioId = (id: string | null) => {
    setState((prev) => ({ ...prev, currentAudioId: id }));
  };

  const setStatus = (status: ProcessingStatus) => {
    setState((prev) => ({ ...prev, status }));
  };

  const setAudioStatus = (audioStatus: AudioStatusResponse | null) => {
    setState((prev) => ({ ...prev, audioStatus }));
  };

  const setSummary = (summary: SummaryResponse | null) => {
    setState((prev) => ({ ...prev, summary }));
  };

  const setError = (error: string | null) => {
    setState((prev) => ({ ...prev, error }));
  };

  const reset = () => {
    setState(initialState);
  };

  return (
    <MeetingContext.Provider
      value={{
        ...state,
        setCurrentAudioId,
        setStatus,
        setAudioStatus,
        setSummary,
        setError,
        reset,
      }}
    >
      {children}
    </MeetingContext.Provider>
  );
}

export function useMeeting() {
  const context = useContext(MeetingContext);
  if (context === undefined) {
    throw new Error('useMeeting must be used within a MeetingProvider');
  }
  return context;
}
