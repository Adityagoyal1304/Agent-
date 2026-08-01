// components/Filmstrip.jsx — Horizontal row of iteration thumbnails
/**
 * Shows a scrollable horizontal strip of attempt thumbnails.
 * Clicking a thumbnail marks it as active and calls onSelect.
 * Props:
 *   items: [{iteration, score, renderSrc}]
 *   activeIndex: number
 *   onSelect: (index) => void
 */
export default function Filmstrip({ items, activeIndex, onSelect }) {
  if (!items || items.length === 0) {
    return (
      <div style={{ color: 'var(--text-dim)', fontSize: '0.78rem', display: 'flex', alignItems: 'center', height: '100%' }}>
        Iteration thumbnails will appear here during the run
      </div>
    );
  }

  function badgeColor(score) {
    if (score >= 85) return 'var(--green)';
    if (score >= 60) return 'var(--amber)';
    return 'var(--red)';
  }

  return (
    <div className="filmstrip-row">
      {items.map((item, idx) => (
        <div
          key={idx}
          className={`filmstrip-cell ${activeIndex === idx ? 'active' : ''}`}
          onClick={() => onSelect(idx)}
        >
          {item.renderSrc ? (
            <img
              src={item.renderSrc.startsWith('data:') ? item.renderSrc : `data:image/png;base64,${item.renderSrc}`}
              alt={`Attempt ${item.iteration}`}
            />
          ) : (
            <div style={{ width: 100, height: 70, background: 'var(--surface2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <span style={{ fontSize: '1.2rem' }}>⏳</span>
            </div>
          )}
          <div className="filmstrip-label" style={{ color: badgeColor(item.score) }}>
            #{item.iteration} · {item.score}
          </div>
        </div>
      ))}
    </div>
  );
}
