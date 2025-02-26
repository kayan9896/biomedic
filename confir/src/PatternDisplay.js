import React, { useState, useEffect } from 'react';
import Circle from './patterns/Circle';
import Arc from './patterns/Arc';
import Ellipse from './patterns/Ellipse';
import Line from './patterns/Line';

const PatternDisplay = ({ metadata, onSave }) => {
  // Create state to track changes to metadata
  const [originalMetadata] = useState(metadata);
  const [currentMetadata, setCurrentMetadata] = useState(metadata);
console.log(currentMetadata)
  // Make methods available to parent component via onSave
  const [resetKey, setResetKey] = useState(0);

  // Set up ref methods

    if (onSave) {
      onSave.current = {
        getCurrentMetadata: () => currentMetadata,
        resetToOriginal: () => {
          console.log("Resetting to original:", originalMetadata);
          setCurrentMetadata({...originalMetadata});
          // Force remount of child components by changing the key
          setResetKey(prev => prev + 1);
        }
      };
    }


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
    position: 'absolute',
    top: '0px',
    zIndex: 5
  };

  return (
    <div style={containerStyle} key={resetKey}>
      {/* Add key={resetKey} to force remount on reset */}
      <Circle 
        key={`circle-${resetKey}`}
        center={currentMetadata.circle.center}
        edgePoint={currentMetadata.circle.edgePoint}
        onCenterChange={(newCenter) => handleCircleUpdate(newCenter, currentMetadata.circle.edgePoint)}
        onEdgePointChange={(newEdge) => handleCircleUpdate(currentMetadata.circle.center, newEdge)}
      />
      
      <Arc 
        key={`arc-${resetKey}`}
        arc={currentMetadata.arc}
        onChange={handleArcUpdate}
      />
      
      <Ellipse 
        key={`ellipse-${resetKey}`}
        ellipse={currentMetadata.ellipse}
        onChange={handleEllipseUpdate}
      />

      <Line 
        key={`line1-${resetKey}`}
        squareSize={960}
        points={currentMetadata.lines.straight}
        onChange={handleStraightLineUpdate}
      />
      <Line 
        key={`line2-${resetKey}`}
        squareSize={960}
        points={currentMetadata.lines.sine}
        onChange={handleSineLineUpdate}
      />
    </div>
  );
};

export default PatternDisplay;