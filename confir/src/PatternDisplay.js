import React, { useState, useEffect } from 'react';
import Circle from './patterns/Circle';
import Arc from './patterns/Arc';
import Ellipse from './patterns/Ellipse';
import Line from './patterns/Line';

const PatternDisplay = ({ metadata, onSave, imageUrl}) => {
  // Create state to track changes to metadata
  const [originalMetadata, setOriginalMetadata] = useState({...metadata}); // Initial backend data - never changes
  const [lastSavedMetadata, setLastSavedMetadata] = useState({...metadata}); // Last saved state
  const [currentMetadata, setCurrentMetadata] = useState({...metadata}); // Current editing state
  const [resetKey, setResetKey] = useState(0);
  useEffect(() => {
    if (metadata) {
      setOriginalMetadata({...metadata});
      setLastSavedMetadata({...metadata});
      setCurrentMetadata({...metadata});
      setResetKey(prev => prev + 1); // Force remount of child components
    }
  }, [metadata]);
  // Update methods exposed via ref
  useEffect(() => {
    if (onSave) {
      onSave.current = {
        // Get current state for saving
        getCurrentMetadata: () => currentMetadata,
        
        // Update last saved metadata when save occurs
        updateSavedMetadata: () => {
          if(currentMetadata){
          setLastSavedMetadata({...currentMetadata});}
          else{setLastSavedMetadata(null)}
        },
        
        // Exit - return to last saved state
        resetToLastSaved: () => {
          console.log("Resetting to last saved state:", lastSavedMetadata);
          if(lastSavedMetadata){setCurrentMetadata({...lastSavedMetadata});}
          else{setCurrentMetadata(null)}
          setResetKey(prev => prev + 1);
        },
        
        // Reset - return to original backend data
        resetToOriginal: () => {
          console.log("Resetting to original state:", originalMetadata);
          setCurrentMetadata({...originalMetadata});
          setResetKey(prev => prev + 1);
        },
        
        // Delete - clear all pattern data
        clearAllPatterns: () => {
          console.log("Clearing all patterns");
          // Define empty/default state for each pattern type
          
          setCurrentMetadata(null);
          setResetKey(prev => prev + 1);
        }
      };
    }
  }, [onSave, currentMetadata, lastSavedMetadata, originalMetadata]);

  

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

  return (<>
    {currentMetadata&&<div style={containerStyle} key={resetKey}>
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
        imageUrl={imageUrl}
      />
      <Line 
        key={`line2-${resetKey}`}
        squareSize={960}
        points={currentMetadata.lines.sine}
        onChange={handleSineLineUpdate}
      />
    </div>}</>
  );
};

export default PatternDisplay;