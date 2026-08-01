// components/CodePanel.jsx — HTML source with copy and download buttons
import { useState } from 'react';
import { downloadBest } from '../api.js';

/**
 * Shows the generated HTML with copy-to-clipboard and download buttons.
 * Props:
 *   html: string
 *   runId: string
 */
export default function CodePanel({ html, runId }) {
  const [copied, setCopied] = useState(false);

  if (!html) return null;

  function copyToClipboard() {
    navigator.clipboard.writeText(html).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  function download() {
    if (runId) {
      downloadBest(runId);
    } else {
      // Fallback: create a Blob download
      const blob = new Blob([html], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'pixelforge_best.html';
      a.click();
      URL.revokeObjectURL(url);
    }
  }

  return (
    <div className="code-panel">
      <div className="code-panel-header">
        <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontFamily: 'JetBrains Mono, monospace' }}>
          best.html — {html.length.toLocaleString()} chars
        </span>
        <div className="code-actions">
          <button className="btn-sm" onClick={copyToClipboard}>
            {copied ? '✓ Copied' : 'Copy'}
          </button>
          <button className="btn-sm primary" onClick={download}>
            ↓ Download
          </button>
        </div>
      </div>
      <div className="code-scroll">
        <pre>{html}</pre>
      </div>
    </div>
  );
}
