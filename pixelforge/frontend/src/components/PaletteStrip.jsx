// components/PaletteStrip.jsx — Display extracted hex colour swatches
/**
 * Shows 6 colour swatches extracted from the target image.
 * Tooltip on hover shows the hex value.
 * Props: palette (string[]) — array of hex strings
 */
export default function PaletteStrip({ palette }) {
  if (!palette || palette.length === 0) {
    return (
      <div style={{ color: 'var(--text-dim)', fontSize: '0.78rem' }}>
        Palette extracted after run starts
      </div>
    );
  }

  return (
    <div className="palette-strip">
      {palette.map((hex, i) => (
        <div
          key={i}
          className="palette-swatch"
          style={{ background: hex }}
          title={hex}
        >
          <span className="palette-hex">{hex}</span>
        </div>
      ))}
    </div>
  );
}
