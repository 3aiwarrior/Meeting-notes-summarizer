/**
 * Main App component with routing.
 */

import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { MeetingProvider } from './context';
import { HomePage, UploadPage, ResultsPage } from './pages';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <MeetingProvider>
        <div className="App">
          <nav className="app-nav">
            <Link to="/" className="nav-logo">
              Meeting Notes Summarizer
            </Link>
            <div className="nav-links">
              <Link to="/">Home</Link>
              <Link to="/upload">Record</Link>
            </div>
          </nav>

          <main className="app-main">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/results/:audioId" element={<ResultsPage />} />
            </Routes>
          </main>

          <footer className="app-footer">
            <p>Meeting Notes Summarizer v0.1.0</p>
          </footer>
        </div>
      </MeetingProvider>
    </BrowserRouter>
  );
}

export default App;
