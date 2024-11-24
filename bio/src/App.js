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

  const tabs = ['measurement', 'report'];

  return (
    <div className="app">
      <div className="tabs" style={{ 
        display: 'flex', 
        marginBottom: '20px',
        position: 'relative',
      }}>
        <TabButton 
          isActive={activeTab === 'measurement'} 
          onClick={() => setActiveTab('measurement')}
        >
          Measurement
        </TabButton>
        <TabButton 
          isActive={activeTab === 'report'} 
          onClick={() => setActiveTab('report')}
        >
          Report
        </TabButton>
      </div>
      <div className="content">
        {activeTab === 'measurement' ? (
          <div className="measurement-view">
            <div className="image-container">
              <ImageMeasurementTool Url="https://legendary-goldfish-qg6rjrrw7gv3xvg4-5000.app.github.dev/" zoom={zoom} />
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
  gap: 0px; /* Remove gap between buttons */
  padding: 20px;
}
// Add some CSS
.tab-button {
  transition: all 0.3s ease;
}

.tab-button:hover:not(.active) path {
  fill: #e0e0e0;
}

.tab-button.active {
  z-index: 2; // Ensure active tab appears above others
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

import buttonImage from './heatmap.jpeg'; // Import your button image

const TabButton = ({ isActive, onClick, children, width = 120, height = 50 }) => {
  return (
    <button
      className={`tab-button ${isActive ? 'active' : ''}`}
      onClick={onClick}
      style={{
        background: 'none',
        border: 'none',
        padding: 0,
        cursor: 'pointer',
        outline: 'none',
        position: 'relative',
        width: `${width}px`,
        height: `${height}px`,
        marginRight: `-${width * 0.2}px`, // Adjust this value to control overlap
      }}
    >
      <img 
        src={buttonImage} 
        alt=""
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          filter: isActive ? 'brightness(1.2)' : 'none', // Optional: makes active tab brighter
        }}
      />
      <span style={{ 
        position: 'relative', 
        zIndex: 1,
        color: isActive ? '#fff' : '#000', // Adjust text color as needed
      }}>
        {children}
      </span>
    </button>
  );
};

