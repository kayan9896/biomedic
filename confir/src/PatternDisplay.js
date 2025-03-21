import React, { useState, useEffect, useRef } from 'react';
import Circle from './patterns/Circle';
import Arc from './patterns/Arc';
import Ellipse from './patterns/Ellipse';
import Line from './patterns/Line';

const PatternDisplay = ({ group, metadata, onSave, isLeftSquare, imageUrl }) => {
  // Keep metadata in array format
  const [originalMetadata, setOriginalMetadata] = useState(metadata[group] || []);
  const [lastSavedMetadata, setLastSavedMetadata] = useState(metadata[group] || []);
  const [currentMetadata, setCurrentMetadata] = useState(metadata[group] || []);
  const [resetKey, setResetKey] = useState(0);
  
  useEffect(() => {
    if (metadata) {
      setOriginalMetadata([...metadata[group]]);
      setLastSavedMetadata([...metadata[group]]);
      setCurrentMetadata([...metadata[group]]);
      setResetKey(prev => prev + 1);
    }
  }, [metadata]);
  
// Register methods with parent via callback
  useEffect(() => {
    if (onSave) {
      onSave({
        getCurrentMetadata: () => {
          const updatedMetadata = { ...metadata, [group]: currentMetadata };
          return updatedMetadata;
        },
        updateSavedMetadata: () => {
          if (currentMetadata && currentMetadata.length > 0) {
            setLastSavedMetadata([...currentMetadata]);
          } else {
            setLastSavedMetadata([]);
          }
        },
        resetToLastSaved: () => {
          console.log("Resetting to last saved state:", lastSavedMetadata);
          if (lastSavedMetadata && lastSavedMetadata.length > 0) {
            setCurrentMetadata([...lastSavedMetadata]);
          } else {
            setCurrentMetadata([]);
          }
          setResetKey(prev => prev + 1);
        },
        resetToOriginal: () => {
          console.log("Resetting to original state:", originalMetadata);
          setCurrentMetadata([...originalMetadata]);
          setResetKey(prev => prev + 1);
        },
        clearAllPatterns: () => {
          console.log("Clearing all patterns");
          setCurrentMetadata([]);
          setResetKey(prev => prev + 1);
        },
      });
    }
  }, [onSave, currentMetadata, lastSavedMetadata, originalMetadata, group, metadata]);

  // Handler to update a specific pattern
  const handlePatternUpdate = (index, newPoints) => {
    setCurrentMetadata(prev => {
      const updated = [...prev];
      updated[index] = {
        ...updated[index],
        points: newPoints
      };
      return updated;
    });
  };


  // Container styles
  const containerStyle = {
    position: 'absolute',
    top: '0px',
    zIndex: 5
  };

  const renderDashedLines = (patterns) => {
    const lines = [];
  
    for (let i = 0; i < patterns.length - 1; i++) {
      const currentPattern = patterns[i];
      const nextPattern = patterns[i + 1];
  
      
        const lastPoint = currentPattern.points[currentPattern.points.length - 1];
        const firstPoint = nextPattern.points[0];
        console.log(lastPoint,firstPoint,currentPattern,nextPattern)
        lines.push(
          <line
            key={`dashed-line-${i}`}
            x1={lastPoint[0]}
            y1={lastPoint[1]}
            x2={firstPoint[0]}
            y2={firstPoint[1]}
            stroke="gray"
            strokeDasharray="5,5"
            strokeWidth={2}
            style={{ position: 'absolute', top: 0, left: 0 }}
          />
        );
      
    }
  
    return lines;
  };

  return (
    <>
      {currentMetadata && currentMetadata.length > 0 && (
        <div style={containerStyle} key={resetKey}>
          <svg 
            width="960" 
            height="960" 
            style={{ 
              position: 'absolute', 
              top: 0, 
              left: 0, 
              pointerEvents: 'none',
              zIndex: 1
            }}
          >
            {renderDashedLines(currentMetadata)}
          </svg>
          {/* Dynamically render components based on metadata type */}
          {currentMetadata.map((pattern, index) => {
            const key = `${pattern.type}-${index}-${resetKey}`;
            
            switch (pattern.type) {
              case 'circle':
                return (
                  <Circle
                    key={key}
                    center={pattern.points.center}
                    edgePoint={pattern.points.edgePoint}
                    onCenterChange={(newCenter) => 
                      handlePatternUpdate(index, {
                        center: newCenter,
                        edgePoint: pattern.points.edgePoint
                      })
                    }
                    onEdgePointChange={(newEdge) => 
                      handlePatternUpdate(index, {
                        center: pattern.points.center,
                        edgePoint: newEdge
                      })
                    }
                    imageUrl={imageUrl}
                    metadata={currentMetadata}
                  />
                );
                
              case 'arc':
                return (
                  <Arc
                    key={key}
                    arc={pattern.points}
                    onChange={(newArc) => handlePatternUpdate(index, newArc)}
                    imageUrl={imageUrl}
                    isLeftSquare={isLeftSquare}
                    metadata={currentMetadata}
                    idx={null}
                  />
                );
                
              case 'ellipse':
                return (
                  <Ellipse
                    key={key}
                    ellipse={pattern.points}
                    onChange={(newEllipse) => handlePatternUpdate(index, newEllipse)}
                    imageUrl={imageUrl}
                    isLeftSquare={isLeftSquare}
                    metadata={currentMetadata}
                    idx={null}
                  />
                );
                
              case 'lines':
                return (
                  <Line
                    key={key}
                    squareSize={960}
                    points={pattern.points}
                    onChange={(newPoints) => handlePatternUpdate(index, newPoints)}
                    imageUrl={imageUrl}
                    isLeftSquare={isLeftSquare}
                    metadata={currentMetadata}
                    idx={null}
                  />
                );
                
              default:
                return null;
            }
          })}
          
          {/* Group control for selected patterns, if at least 2 are selected */}
          {
            <PatternGroupManager
              patterns={currentMetadata}
              onPatternsUpdate={handleMultiplePatternsUpdate}
              handle={metadata[group][0]['handle']}
            />
          }
        </div>
      )}
    </>
  );

  // Function to update multiple patterns at once (for group movement)
  function handleMultiplePatternsUpdate(updatedPatterns) {
    setCurrentMetadata(prev => {
      const newMetadata = [...prev];
      updatedPatterns.forEach((pattern, i) => {
        newMetadata[i] = pattern;
      });
      return newMetadata;
    });
  }
};

// New component for managing groups of selected patterns
const PatternGroupManager = ({ patterns, onPatternsUpdate, handle }) => {
  const [controlPoint, setControlPoint] = useState(handle);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState(null);
  const [initialPatterns, setInitialPatterns] = useState([]);
  const groupRef = useRef(null);

  useEffect(() => {
    setInitialPatterns(patterns);
  }, [patterns]);

  useEffect(() => {
    const handleGlobalMove = (e) => {
      if (!isDragging) return;
      
      e.preventDefault();
      const event = e.touches ? e.touches[0] : e;
      const rect = groupRef.current.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      
      // Calculate movement delta
      const dx = x - dragStart[0];
      const dy = y - dragStart[1];
      
      // Update control point position
      setControlPoint([controlPoint[0] + dx, controlPoint[1] + dy]);
      
      // Create updated versions of all selected patterns
      const updatedPatterns = initialPatterns.map(pattern => {
        const newPattern = { ...pattern };

        // Update points based on pattern type
        if (pattern.type === 'circle') {
          newPattern.points = {
            center: [pattern.points.center[0] + dx, pattern.points.center[1] + dy],
            edgePoint: [pattern.points.edgePoint[0] + dx, pattern.points.edgePoint[1] + dy]
          };
        } 
        else if (pattern.type === 'lines') {
          // For line patterns, move all points
          newPattern.points = pattern.points.map(point => [
            point[0] + dx, point[1] + dy
          ]);
        }
        else {
          // For arc, ellipse, and any other patterns with array points
          newPattern.points = pattern.points.map(point => [
            point[0] + dx, point[1] + dy
          ]);
        }
        return newPattern;
      });
      
      // Update all patterns at once
      onPatternsUpdate(updatedPatterns);
      
      // Update drag start position for next move
      setDragStart([x, y]);
      
      // Also update the initial positions for next move
      setInitialPatterns(updatedPatterns);
    };

    const handleGlobalUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleGlobalMove);
      document.addEventListener('mouseup', handleGlobalUp);
      document.addEventListener('touchmove', handleGlobalMove);
      document.addEventListener('touchend', handleGlobalUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleGlobalMove);
      document.removeEventListener('mouseup', handleGlobalUp);
      document.removeEventListener('touchmove', handleGlobalMove);
      document.removeEventListener('touchend', handleGlobalUp);
    };
  }, [isDragging, dragStart, controlPoint, initialPatterns, onPatternsUpdate]);

  function handleMouseDown(e) {
    e.preventDefault();
    e.stopPropagation();
    
    const event = e.touches ? e.touches[0] : e;
    const rect = groupRef.current.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    setIsDragging(true);
    setDragStart([x, y]);
  }

  return (
    <svg 
      ref={groupRef}
      width="960" 
      height="960"
      style={{ 
        position: 'absolute', 
        top: 0, 
        left: 0, 
        pointerEvents: 'none'
      }}
    >
      <g pointerEvents="auto">
        <circle
          cx={controlPoint[0]}
          cy={controlPoint[1]}
          r={15}
          fill="rgba(0, 200, 0, 0.7)"
          stroke="white"
          strokeWidth="2"
          cursor={isDragging ? 'grabbing' : 'grab'}
          onMouseDown={handleMouseDown}
          onTouchStart={handleMouseDown}
        />
        <circle
          cx={controlPoint[0]}
          cy={controlPoint[1]}
          r={25}
          fill="transparent"
          stroke="rgba(0, 200, 0, 0.3)"
          strokeWidth="2"
          strokeDasharray="5,5"
          pointerEvents="none"
        />
        <text
          x={controlPoint[0]}
          y={controlPoint[1] + 35}
          textAnchor="middle"
          fill="green"
          fontSize="12"
          pointerEvents="none"
        >
          Group
        </text>
      </g>
    </svg>
  );
};

export default PatternDisplay;

