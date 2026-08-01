// App.jsx — PixelForge main application
// Layout: upload + target on left | iteration feed on right | filmstrip at bottom
import { useState, useRef, useEffect } from 'react';

import UploadZone from './components/UploadZone.jsx';
import PaletteStrip from './components/PaletteStrip.jsx';
import StatusBar from './components/StatusBar.jsx';
import IterationCard from './components/IterationCard.jsx';
import Filmstrip from './components/Filmstrip.jsx';
import LivePreview from './components/LivePreview.jsx';
import CodePanel from './components/CodePanel.jsx';

import { createRun, streamRun } from './api.js';

import './index.css';

const MAX_ITERATIONS = 5;

export default function App() {
  const [file, setFile] = useState(null);
  const [runId, setRunId] = useState(null);
  const [status, setStatus] = useState('idle'); // 'idle' | 'running' | 'done' | 'error'
  const [statusMsg, setStatusMsg] = useState('');
  const [palette, setPalette] = useState([]);
  const [iterations, setIterations] = useState([]); // [{iteration, score, renderSrc, discrepancies, summary}]
  const [bestHtml, setBestHtml] = useState('');
  const [bestScore, setBestScore] = useState(0);
  const [bestIteration, setBestIteration] = useState(0);
  const [activeFilmstrip, setActiveFilmstrip] = useState(null);
  const [targetSrc, setTargetSrc] = useState(null); // object URL of uploaded file

  const esRef = useRef(null);
  const feedRef = useRef(null);

  // Clean up EventSource on unmount
  useEffect(() => {
    return () => { if (esRef.current) esRef.current.close(); };
  }, []);

  function onFileSelected(f) {
    setFile(f);
    setTargetSrc(URL.createObjectURL(f));
    // Reset run state when a new file is picked
    setIterations([]);
    setBestHtml('');
    setBestScore(0);
    setBestIteration(0);
    setPalette([]);
    setRunId(null);
    setStatus('idle');
  }

  async function startRun() {
    if (!file || status === 'running') return;

    setStatus('running');
    setStatusMsg('Uploading image...');
    setIterations([]);
    setBestHtml('');
    setBestScore(0);
    setPalette([]);

    try {
      const { run_id } = await createRun(file);
      setRunId(run_id);
      setStatusMsg('Extracting palette and generating HTML...');

      // Open SSE stream
      esRef.current = streamRun(
        run_id,
        (data) => handleSSEEvent(data),
        (err) => {
          console.error('SSE error:', err);
          setStatus('error');
          setStatusMsg('Connection error — check that the backend is running');
        }
      );
    } catch (err) {
      console.error('Run error:', err);
      setStatus('error');
      setStatusMsg(`Error: ${err.message}`);
    }
  }

  function handleSSEEvent(data) {
    if (data.error) {
      setStatus('error');
      setStatusMsg(`Error: ${data.error}`);
      return;
    }

    // Extract palette from first iteration event
    if (data.palette && data.palette.length > 0) {
      setPalette(data.palette);
    }

    if (data.node === 'done' || data.done) {
      // Final event
      const finalScore = data.best_score || data.score || 0;
      setBestHtml(data.html || '');
      setBestScore(finalScore);
      setBestIteration(data.best_iteration || data.iteration || 0);
      setStatus('done');
      setStatusMsg(`Complete! Best score: ${finalScore}/100`);

      // Add final iteration card if not already there
      if (data.node === 'done') return;
    }

    if (data.node === 'keep_best' || (data.iteration && data.score !== undefined)) {
      // New iteration completed — append card
      const newEntry = {
        iteration: data.iteration,
        score: data.score,
        renderSrc: data.render_b64 || null,
        discrepancies: data.discrepancies || [],
        summary: data.summary || '',
      };

      setIterations(prev => {
        // Avoid duplicates
        const existing = prev.find(i => i.iteration === data.iteration);
        if (existing) return prev;
        const updated = [...prev, newEntry];
        setActiveFilmstrip(updated.length - 1);
        return updated;
      });

      if (data.html) {
        setBestHtml(data.html);
        setBestScore(data.best_score || data.score);
        setBestIteration(data.best_iteration || data.iteration);
      }

      setStatusMsg(`Attempt ${data.iteration} scored ${data.score}/100`);

      // Auto-scroll feed to show new card
      setTimeout(() => {
        feedRef.current?.lastElementChild?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  }

  const currentIteration = iterations.length + (status === 'running' ? 1 : 0);

  return (
    <div className="app-shell">
      {/* ===== HEADER ===== */}
      <header className="app-header">
        <div className="logo">
          <div className="logo-mark">⚡</div>
          <div className="logo-text">Shot<span>2Code</span></div>
        </div>
        <span className="header-sub">
          Screenshot → HTML · Self-correcting AI loop
        </span>
      </header>

      {/* ===== SIDEBAR ===== */}
      <aside className="sidebar">
        <div className="sidebar-section">
          <h3>Target Screenshot</h3>
          <UploadZone onFile={onFileSelected} disabled={status === 'running'} />
        </div>

        <div className="sidebar-section">
          <h3>Colour Palette</h3>
          <PaletteStrip palette={palette} />
        </div>

        <div className="sidebar-section">
          <h3>Run Status</h3>
          <StatusBar
            status={status}
            message={statusMsg}
            current={currentIteration}
            total={5}
          />
        </div>

        <div className="sidebar-section">
          <button
            className="btn-run"
            onClick={startRun}
            disabled={!file || status === 'running'}
          >
            {status === 'running' ? '⏳ Running...' : status === 'done' ? '↺ Run Again' : '▶ Start Run'}
          </button>
        </div>

        {/* Live preview in sidebar for best result */}
        {bestHtml && (
          <div className="sidebar-section" style={{ flex: 1, overflow: 'hidden' }}>
            <h3>Best Output</h3>
            <LivePreview
              html={bestHtml}
              bestScore={bestScore}
              bestIteration={bestIteration}
            />
          </div>
        )}

        {/* Code panel */}
        {bestHtml && (
          <div className="sidebar-section">
            <CodePanel html={bestHtml} runId={runId} />
          </div>
        )}
      </aside>

      {/* ===== MAIN FEED ===== */}
      <main className="main-feed" ref={feedRef}>
        {iterations.length === 0 && status !== 'running' && (
          <div className="empty-state" style={{ height: '100%' }}>
            <div className="empty-icon">🔮</div>
            <div className="empty-text">
              Upload a screenshot, hit Start Run, and watch Shot2Code iterate toward pixel-perfect HTML
            </div>
          </div>
        )}

        {iterations.length === 0 && status === 'running' && (
          <div className="empty-state" style={{ height: '100%' }}>
            <div className="empty-icon" style={{ animation: 'pulse 1.5s infinite' }}>⚙️</div>
            <div className="empty-text">Generating first attempt...</div>
          </div>
        )}

        {/* Iteration cards append as SSE events arrive */}
        {iterations.map((it, idx) => (
          <IterationCard
            key={it.iteration}
            iteration={it.iteration}
            score={it.score}
            targetSrc={targetSrc}
            renderSrc={it.renderSrc}
            discrepancies={it.discrepancies}
            summary={it.summary}
          />
        ))}
      </main>

      {/* ===== FILMSTRIP ===== */}
      <footer className="filmstrip-area">
        <Filmstrip
          items={iterations}
          activeIndex={activeFilmstrip}
          onSelect={setActiveFilmstrip}
        />
      </footer>
    </div>
  );
}
