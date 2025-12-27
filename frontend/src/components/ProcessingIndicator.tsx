/**
 * ProcessingIndicator component.
 *
 * Shows upload and processing status.
 */

import type { ProcessingStatus } from '../types';

interface ProcessingIndicatorProps {
  status: ProcessingStatus;
}

export function ProcessingIndicator({ status }: ProcessingIndicatorProps) {
  return (
    <div className="processing-indicator">
      <div className="spinner"></div>
      <p className="processing-message">
        {status === 'uploading' && 'Uploading audio...'}
        {status === 'processing' && 'Processing your meeting (transcription + summarization)...'}
      </p>
      <p className="processing-note">This may take a minute or two</p>
    </div>
  );
}
