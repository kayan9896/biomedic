import React, { useState } from 'react';
import ImageMeasurementTool from './ImageMeasurementTool';
import ControlPanel from './ControlPanel';
import Report from './Report';
import imageFile from './gf.gif';

function App() {
  const [activeTab, setActiveTab] = useState('measurement');
  const [zoom, setZoom] = useState(1);

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 0.1, 2));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 0.1, 0.5));
  };

  return (
    <div className="app">
      <div className="tabs">
        <button 
          className={activeTab === 'measurement' ? 'active' : ''} 
          onClick={() => setActiveTab('measurement')}
        >
          Measurement
        </button>
        <button 
          className={activeTab === 'report' ? 'active' : ''} 
          onClick={() => setActiveTab('report')}
        >
          Report
        </button>
      </div>

      <div className="content">
        {activeTab === 'measurement' ? (
          <div className="measurement-view">
            <div className="image-container">
              <ImageMeasurementTool imageUrl={imageFile} zoom={zoom} />
            </div>
            <ControlPanel onZoomIn={handleZoomIn} onZoomOut={handleZoomOut} />
          </div>
        ) : (
          <Report />
        )}
      </div>

      <style jsx>{`
        .app {
          display: flex;
          flex-direction: column;
          height: 100vh;
        }
        .tabs {
          display: flex;
          gap: 10px;
          padding: 10px;
          background-color: #f0f0f0;
        }
        .tabs button {
          padding: 10px 20px;
          border: none;
          background: none;
          cursor: pointer;
        }
        .tabs button.active {
          background-color: #007bff;
          color: white;
          border-radius: 4px;
        }
        .content {
          flex: 1;
          overflow: hidden;
        }
        .measurement-view {
          display: flex;
          height: 100%;
        }
        .image-container {
          flex: 1;
          padding: 20px;
          overflow: auto;
          background-color: #eee;
          display: flex;
          justify-content: center;
          align-items: flex-start;
        }
      `}</style>
    </div>
  );
}

export default App;