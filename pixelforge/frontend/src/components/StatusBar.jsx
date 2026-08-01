// components/StatusBar.jsx — Shows current graph node status
/**
 * Displays a live status message with an animated dot.
 * Props:
 *   status: 'idle' | 'running' | 'done' | 'error'
 *   message: string
 *   iteration: number
 *   maxIterations: number
 */
export default function StatusBar({ status, message, iteration, maxIterations }) {
  const label = message || (
    status === 'idle' ? 'Upload an image to start' :
    status === 'running' ? `Attempt ${iteration} of ${maxIterations}...` :
    status === 'done' ? 'Run complete' :
    'Error occurred'
  );

  return (
    <div className="status-bar">
      <div className={`status-dot ${status}`} />
      <span style={{ color: 'var(--text)', fontSize: '0.82rem' }}>{label}</span>
      {status === 'running' && (
        <span style={{ marginLeft: 'auto', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
          {iteration}/{maxIterations}
        </span>
      )}
    </div>
  );
}
