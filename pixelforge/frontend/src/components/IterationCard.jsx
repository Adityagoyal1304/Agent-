// components/IterationCard.jsx — Shows target vs attempt side by side
/**
 * One card per completed iteration. Shows:
 *  - Target image (always the same)
 *  - Rendered attempt screenshot
 *  - Score badge (colour-coded)
 *  - Discrepancy list with severity and fix instructions
 *  - Summary sentence
 *
 * Props:
 *   iteration: number
 *   score: number
 *   targetSrc: string (data URL or base64)
 *   renderSrc: string (data URL or base64)
 *   discrepancies: array
 *   summary: string
 */
export default function IterationCard({
  iteration, score, targetSrc, renderSrc, discrepancies, summary
}) {
  // Colour-code the score badge
  const badgeClass = score >= 85 ? 'green' : score >= 60 ? 'amber' : 'red';

  function sevClass(sev) {
    if (sev >= 5) return 'sev5';
    if (sev >= 3) return 'sev3';
    return 'sev1';
  }

  return (
    <div className="iteration-card">
      <div className="iteration-card-header">
        <span className="iteration-label">Attempt #{iteration}</span>
        <span className={`score-badge ${badgeClass}`}>{score}/100</span>
      </div>

      {/* Side-by-side images */}
      <div className="iteration-images">
        <div className="img-panel">
          <div className="img-panel-label">Target</div>
          {targetSrc ? (
            <img src={targetSrc.startsWith('data:') ? targetSrc : `data:image/png;base64,${targetSrc}`} alt="Target" />
          ) : (
            <div style={{ height: 120, background: 'var(--surface2)', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-dim)', fontSize: '0.75rem' }}>
              No image
            </div>
          )}
        </div>
        <div className="img-panel">
          <div className="img-panel-label">Attempt</div>
          {renderSrc ? (
            <img src={renderSrc.startsWith('data:') ? renderSrc : `data:image/png;base64,${renderSrc}`} alt={`Attempt ${iteration}`} />
          ) : (
            <div style={{ height: 120, background: 'var(--surface2)', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-dim)', fontSize: '0.75rem' }}>
              Rendering...
            </div>
          )}
        </div>
      </div>

      {/* Summary */}
      {summary && <div className="iteration-summary">"{summary}"</div>}

      {/* Discrepancies */}
      {discrepancies && discrepancies.length > 0 && (
        <div className="discrepancy-list">
          {discrepancies.map((d, i) => (
            <div key={i} className="discrepancy-item">
              <div className={`disc-severity ${sevClass(d.severity)}`}>{d.severity}</div>
              <div className="disc-body">
                <div className="disc-region">{d.region}</div>
                <div className="disc-issue">{d.issue}</div>
                <span className="disc-fix">{d.fix}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
