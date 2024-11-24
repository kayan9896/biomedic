import React, { useState } from 'react';

function ControlPanel({ onZoomIn, onZoomOut, isMoving = false }) {
  const[p,setp]=useState(true)
  return (
    <div className="control-panel">
      <h3>Controls</h3>
      <div className="button-group">
        <button onClick={onZoomIn}>Zoom In (+)</button>
        <button onClick={onZoomOut}>Zoom Out (-)</button>
      </div>
      <button onClick={()=>setp(!p)}>move</button>
      <div className="status-indicator">
        <div className={`status-circle ${p ? 'moving' : 'stationary'}`}>
          <div className="inner-circle">
            <span className="status-text">
              {isMoving ? 'Moving' : 'Stationary'}
            </span>
          </div>
        </div>
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
          margin-bottom: 20px;
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
        .status-indicator {
          display: flex;
          justify-content: center;
          margin-top: 20px;
        }
        .status-circle {
          width: 120px;
          height: 120px;
          border-radius: 50%;
          position: relative;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 10px; /* This creates the thick ring effect */
        }
        .status-circle.moving {
          background-color: #007bff; /* Blue ring */
        }
        .status-circle.stationary {
          background-color: #28a745; /* Green for stationary */
        }
        .inner-circle {
          width: 100%;
          height: 100%;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .status-circle.moving .inner-circle {
          background-color: #dc3545; /* Red circle for moving */
        }
        .status-circle.stationary .inner-circle {
          background-color: #28a745; /* Green circle for stationary */
        }
        .status-text {
          color: white;
          font-size: 16px;
          font-weight: bold;
          text-align: center;
        }
      `}</style>
    </div>
  );
}

export default ControlPanel;