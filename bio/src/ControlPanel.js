import React from 'react';

function ControlPanel({ onZoomIn, onZoomOut }) {
  return (
    <div className="control-panel">
      <h3>Controls</h3>
      <div className="button-group">
        <button onClick={onZoomIn}>Zoom In (+)</button>
        <button onClick={onZoomOut}>Zoom Out (-)</button>
      </div>
      <style jsx>{`
        .control-panel {
          padding: 20px;
          background-color: #f5f5f5;
          border-left: 1px solid #ddd;
          height: 100%;
        }
        .button-group {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        button {
          padding: 10px;
          background-color: #007bff;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }
        button:hover {
          background-color: #0056b3;
        }
      `}</style>
    </div>
  );
}

export default ControlPanel;