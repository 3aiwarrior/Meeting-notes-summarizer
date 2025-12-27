/**
 * SummaryDisplay component.
 *
 * Displays meeting summary with structured data.
 */

import type { SummaryResponse } from '../types';

interface SummaryDisplayProps {
  summary: SummaryResponse;
}

export function SummaryDisplay({ summary }: SummaryDisplayProps) {
  return (
    <div className="summary-display">
      <h2>Meeting Summary</h2>

      {summary.summary_text && (
        <div className="summary-section">
          <h3>Overview</h3>
          <p className="summary-text">{summary.summary_text}</p>
        </div>
      )}

      {summary.key_points && summary.key_points.length > 0 && (
        <div className="summary-section">
          <h3>Key Points</h3>
          <ul className="key-points-list">
            {summary.key_points.map((point, index) => (
              <li key={index}>{point}</li>
            ))}
          </ul>
        </div>
      )}

      {summary.action_items && summary.action_items.length > 0 && (
        <div className="summary-section">
          <h3>Action Items</h3>
          <ul className="action-items-list">
            {summary.action_items.map((item, index) => (
              <li key={index}>
                <strong>{item.item}</strong>
                {item.owner && ` - ${item.owner}`}
              </li>
            ))}
          </ul>
        </div>
      )}

      {summary.decisions && summary.decisions.length > 0 && (
        <div className="summary-section">
          <h3>Decisions Made</h3>
          <ul className="decisions-list">
            {summary.decisions.map((decision, index) => (
              <li key={index}>{decision}</li>
            ))}
          </ul>
        </div>
      )}

      {summary.participants && summary.participants.length > 0 && (
        <div className="summary-section">
          <h3>Participants</h3>
          <div className="participants-list">
            {summary.participants.map((participant, index) => (
              <span key={index} className="participant-badge">
                {participant}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="summary-meta">
        <span>Model: {summary.model_used}</span>
        {summary.tokens_used && <span> • Tokens: {summary.tokens_used.toLocaleString()}</span>}
      </div>
    </div>
  );
}
