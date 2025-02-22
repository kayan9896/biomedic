import React, { useState } from 'react';
import Circle from './patterns/Circle';
import Arc from './patterns/Arc';
import Ellipse from './patterns/Ellipse';
import Line from './patterns/Line';

const PatternDisplay = ({ metadata }) => {
  // Create state to track changes to metadata
  const [currentMetadata, setCurrentMetadata] = useState(metadata);
console.log(currentMetadata)
  // Update handlers for each pattern type
  const handleCircleUpdate = (newCenter, newEdgePoint) => {
    setCurrentMetadata(prev => ({
      ...prev,
      circle: {
        center: newCenter,
        edgePoint: newEdgePoint
      }
    }));
  };

  const handleArcUpdate = (newArc) => {
    setCurrentMetadata(prev => ({
      ...prev,
      arc: newArc
    }));
  };

  const handleEllipseUpdate = (newEllipse) => {
    setCurrentMetadata(prev => ({
      ...prev,
      ellipse: newEllipse
    }));
  };

  const handleStraightLineUpdate = (newPoints) => {
    setCurrentMetadata(prev => ({
      ...prev,
      lines: {
        ...prev.lines,
        straight: newPoints
      }
    }));
  };

  const handleSineLineUpdate = (newPoints) => {
    setCurrentMetadata(prev => ({
      ...prev,
      lines: {
        ...prev.lines,
        sine: newPoints
      }
    }));
  };

  // Container styles
  const containerStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 300px)',
    gridTemplateRows: 'repeat(2, 300px)',
    gap: '10px',
    position: 'absolute',
    top: '20px',
    left: '20px',
    zIndex: 5
  };

  return (
    <div style={containerStyle}>
      {/* Circle Box */}
    
        <Circle 
          center={currentMetadata.circle.center}
          edgePoint={currentMetadata.circle.edgePoint}
          onCenterChange={(newCenter) => handleCircleUpdate(newCenter, currentMetadata.circle.edgePoint)}
          onEdgePointChange={(newEdge) => handleCircleUpdate(currentMetadata.circle.center, newEdge)}
        />
      
        <Arc 
          arc={currentMetadata.arc}
          onChange={handleArcUpdate}
        />
      
        <Ellipse 
          ellipse={currentMetadata.ellipse}
          onChange={handleEllipseUpdate}
        />

        <Line 
          squareSize={960}
          points={currentMetadata.lines.straight}
          onChange={handleStraightLineUpdate}
        />
        <Line 
          squareSize={960}
          points={currentMetadata.lines.sine}
          onChange={handleSineLineUpdate}
        />
    </div>
  );
};

export default PatternDisplay;