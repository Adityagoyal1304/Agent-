// components/UploadZone.jsx — Drag-and-drop target image uploader
import { useState, useRef } from 'react';

/**
 * UploadZone handles file selection via click or drag-and-drop.
 * Shows a preview of the target image once selected.
 * Props: onFile(file) called when user picks an image.
 */
export default function UploadZone({ onFile, disabled }) {
  const [dragOver, setDragOver] = useState(false);
  const [preview, setPreview] = useState(null);
  const inputRef = useRef(null);

  function handleFile(file) {
    if (!file || !file.type.startsWith('image/')) return;
    setPreview(URL.createObjectURL(file));
    onFile(file);
  }

  function onDrop(e) {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    handleFile(file);
  }

  function onInputChange(e) {
    handleFile(e.target.files[0]);
  }

  return (
    <div>
      <div
        className={`upload-zone ${dragOver ? 'drag-over' : ''} ${disabled ? 'disabled' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        onClick={() => !disabled && inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          onChange={onInputChange}
          disabled={disabled}
          style={{ display: 'none' }}
        />
        <div className="upload-icon">🖼️</div>
        <div className="upload-title">Drop your screenshot here</div>
        <div className="upload-sub">PNG, JPG, WebP — any resolution</div>
      </div>

      {preview && (
        <div className="target-preview">
          <img src={preview} alt="Target screenshot" />
        </div>
      )}
    </div>
  );
}
