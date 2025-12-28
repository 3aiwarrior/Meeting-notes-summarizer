/**
 * HomePage component - Landing page.
 */

import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui';

export function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="home-page">
      <div className="hero-section">
        <h1>Meeting Notes Summarizer</h1>
        <p className="hero-subtitle">
          Transform your meetings into actionable insights with AI-powered transcription and summarization.
        </p>

        <div className="features-list">
          <div className="feature-item">
            <span className="feature-icon">🎙️</span>
            <h3>Record or Upload</h3>
            <p>Record live meetings or upload audio files</p>
          </div>
          <div className="feature-item">
            <span className="feature-icon">📝</span>
            <h3>AI Transcription</h3>
            <p>Accurate transcription powered by OpenAI Whisper</p>
          </div>
          <div className="feature-item">
            <span className="feature-icon">✨</span>
            <h3>Smart Summaries</h3>
            <p>Get key points, action items, and decisions</p>
          </div>
        </div>

        <Button
          variant="primary"
          size="lg"
          onClick={() => navigate('/upload')}
        >
          Get Started
        </Button>
      </div>
    </div>
  );
}
