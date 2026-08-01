// components/LivePreview.jsx — Renders best HTML in an iframe
/**
 * Shows the best HTML live in a sandboxed iframe using srcDoc.
 * Updates in real time as new best HTML arrives via SSE.
 * Props: html (string)
 */
export default function LivePreview({ html, bestScore, bestIteration }) {
  if (!html) {
    return (
      <div className="live-preview-wrapper" style={{ background: 'var(--surface2)', display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 300, borderRadius: 12, border: '1px solid var(--border)' }}>
        <div className="empty-state">
          <div className="empty-icon">🖥️</div>
          <div className="empty-text">Live preview will appear here once the first iteration completes</div>
        </div>
      </div>
    );
  }

  return (
    <div className="live-preview-wrapper">
      <div className="preview-header">
        <span>Live Preview — Best HTML</span>
        {bestScore !== undefined && (
          <span style={{ color: bestScore >= 85 ? 'var(--green)' : bestScore >= 60 ? 'var(--amber)' : 'var(--red)', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
            {bestScore}/100 · iteration {bestIteration}
          </span>
        )}
      </div>
      {/* sandbox prevents the generated HTML from accessing parent window */}
      <iframe
        srcDoc={html}
        sandbox="allow-scripts"
        title="Live HTML Preview"
      />
    </div>
  );
}
