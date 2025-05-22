import React, { useState, useEffect, useRef } from 'react';
import Circle from './patterns/Circle';
import Arc from './patterns/Arc';
import Ellipse from './patterns/Ellipse';
import Line from './patterns/Line';

const PatternDisplay = ({ group, metadata, onSave, isLeftSquare, imageUrl, editing }) => {
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
        setTmp: (template) => {
          console.log("setting template:", template, group, template[group]);
          setCurrentMetadata(template[group]);
          setResetKey(prev => prev + 1);
        },
        clearAllPatterns: (template) => {
          console.log(template,currentMetadata,"tmp");
          setCurrentMetadata(template[group]);
          console.log(currentMetadata,'cur')
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
        points: newPoints,
        template: 0
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
        //console.log(lastPoint,firstPoint,currentPattern,nextPattern)
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
                    colour={currentMetadata[index].template?'FF0000':pattern.colour}
                    onChange={(newArc) => handlePatternUpdate(index, newArc)}
                    imageUrl={imageUrl}
                    isLeftSquare={isLeftSquare}
                    metadata={currentMetadata}
                    idx={null}
                    editing={editing}
                  />
                );
                
              case 'ellipse':
                return (
                  <Ellipse
                    key={key}
                    ellipse={pattern.points}
                    colour={currentMetadata[index].template?'FF0000':pattern.colour}
                    onChange={(newEllipse) => handlePatternUpdate(index, newEllipse)}
                    imageUrl={imageUrl}
                    isLeftSquare={isLeftSquare}
                    metadata={currentMetadata}
                    idx={null}
                    editing={editing}
                  />
                );
                
              case 'lines':
                return (
                  <Line
                    key={key}
                    squareSize={960}
                    points={pattern.points}
                    colour={currentMetadata[index].template?'FF0000':pattern.colour}
                    onChange={(newPoints) => handlePatternUpdate(index, newPoints)}
                    imageUrl={imageUrl}
                    isLeftSquare={isLeftSquare}
                    metadata={currentMetadata}
                    idx={null}
                    editing={editing}
                  />
                );
                
              default:
                return null;
            }
          })}
          
          {/* Group control for selected patterns, if at least 2 are selected */}
          {
            editing&&<PatternGroupManager
              patterns={currentMetadata}
              onPatternsUpdate={handleMultiplePatternsUpdate}
              handle={currentMetadata[0]['handle']}
              group={group}
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
        newMetadata[i]['template']=0
      });
      return newMetadata;
    });
  }
};

// New component for managing groups of selected patterns
const PatternGroupManager = ({ patterns, onPatternsUpdate, handle, group }) => {
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
    <div 
      ref={groupRef}
      style={{ 
        position: 'absolute', 
        top: 0, 
        left: 0,
        width: '960px',
        height: '960px',
        pointerEvents: 'none'
      }}
    >
      {/* Label background with centered text */}
      <div style={{
        position: 'absolute',
        left: `${controlPoint[0]}px`,
        top: `${controlPoint[1] - 50}px`, // Position above the handle
        transform: 'translateX(-50%)',
        pointerEvents: 'none',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}>
        <div style={{
          position: 'relative',
          width: '69px', 
          height: '26px'
        }}>
          <img 
            src={require("./LandmarkLabel.png")} 
            style={{
              position: 'absolute',
              width: '100%',
              height: '100%'
            }}
          />
          <div style={{
            position: 'absolute',
            width: '100%',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100%',
            color: 'white',
            fontSize: '25px',
            fontFamily: 'abel',
            fontWeight: 'bold',
            textAlign: 'center'
          }}>
            {group}
          </div>
        </div>
      </div>
      
      {/* Handle image */}
      <img 
        src={require("./LandmarkHandle.png")} 
        onMouseDown={handleMouseDown}
        onTouchStart={handleMouseDown}
        style={{
          position: 'absolute',
          width: '30px',
          height: '30px',
          left: `${controlPoint[0] - 15}px`,
          top: `${controlPoint[1] - 15}px`,
          cursor: isDragging ? 'grabbing' : 'grab',
          pointerEvents: 'auto'
        }}
      />
    </div>
  );
};

export default PatternDisplay;

