import React, { useRef, useEffect, useState } from 'react';
import Circle from './Circle';
import Arc from './Arc';
import Ellipse from './Ellipse';
import Line from './Line';

const Magnifier = ({ 
  segment,
  group,
  show, 
  imageUrl, 
  magnification = 2,
  size = 380,
  position: { x, y } ,
  metadata,
  isLeftSquare,
  idx,
  filter,
  activeGroup,
  activeSegment
}) => {
    
    const [magnifierPosition, setMagnifierPosition] = useState('default');
    const proximityThreshold = 270; // Distance in pixels to trigger position change
    
    // Calculate magnifier's absolute position
    const getMagnifierCoordinates = () => {
      // For left square
      if (isLeftSquare) {
        // Default is top-left corner
        if (magnifierPosition === 'default') {
          return { top: 0, left: 0 };
        } 
        // Alternate position is top-right corner
        else {
          return { top: 0, left: 960 - size };
        }
      } 
      // For right square
      else {
        // Default is top-right corner
        if (magnifierPosition === 'default') {
          return { top: 0, left: 960 - size };
        } 
        // Alternate position is top-left corner
        else {
          return { top: 0, left: 0 };
        }
      }
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
  
    // Get current coordinates
    const coordinates = getMagnifierCoordinates();
    
    // Check distance between cursor and magnifier
    useEffect(() => {
      if (!show) return;
      
      // Calculate center of magnifier
      const magnifierCenterX = isLeftSquare? (magnifierPosition === 'default' ? size/2 : 960-size/2) : (magnifierPosition === 'default' ? 960-size/2 : size/2);
      const magnifierCenterY =  size/2;
      
      // Calculate distance between cursor and magnifier center
      const distanceX = Math.abs(magnifierCenterX - x)
      const distanceY = Math.abs(magnifierCenterY - y)
      
      
      // Switch position if cursor is too close
      if (distanceX < size / 2 + 50 && distanceY < size / 2 + 50) {
        setMagnifierPosition(magnifierPosition === 'default' ? 'alternate' : 'default');
      } 
    }, [x, y, show]);

  const magnificationLevel = 2;
  const magnifierSize = size;
  const [i,seti] =useState(idx)
  const [currentSegment, setCurrentSegment] = useState(segment)
  useEffect(()=>{
    seti(idx)
    setCurrentSegment(segment)
  },[idx, segment])
  if (!show) return null;
  

  return (
    <div 
      style={{
        position: 'absolute',
        top: coordinates.top,
        left: coordinates.left,
        width: size,
        height: size,
        zIndex: 1000,
        backgroundColor: 'white',
        boxShadow: '0 0 10px rgba(0, 0, 0, 0.5)',
        border: '1px solid #ccc',
        overflow: 'hidden',
        pointerEvents: 'none' // Don't interfere with mouse events
      }}
    >
      
      <div
            style={{
              width: `${480 * magnificationLevel}px`,
              height: `${480 * magnificationLevel}px`,
              transform: `scale(${magnificationLevel})`,
              transformOrigin: `${0}px ${0}px`,
              position: 'absolute',
              left: `${-x * (magnificationLevel - 1) - (x - magnifierSize/2)}px`,
              top: `${-y * (magnificationLevel - 1) - (y - magnifierSize/2)}px`
            }}
          >
            <img src={imageUrl} alt="Image 1" style={{ width: '100%', height: 'auto', ...filter }} />
            {metadata && Object.keys(metadata).map((g, num) => 
            { return(
              <>
              <svg 
                width="960" 
                height="960" 
                style={{ 
                  position: 'absolute', 
                  top: 0, 
                  left: 0, 
                  pointerEvents: 'none',
                }}
              >
              {renderDashedLines(metadata[g])}
              </svg>
              {metadata[g].map((pattern, index) => {
            const key = `${pattern.type}-${index}-${Math.random()}`;

            switch (pattern.type) {
              case 'circle':
                return (
                  <Circle
                    key={key}
                    center={pattern.points.center}
                    edgePoint={pattern.points.edgePoint}

                    imageUrl={imageUrl}
                    metadata={metadata}
                  />
                );
                
              case 'arc':
                return (
                  <Arc
                    key={key}
                    arc={pattern.points}
                    colour={pattern.template?'FF0000':pattern.colour}
                    imageUrl={imageUrl}
                    metadata={metadata[g]}
                    idx={currentSegment === index && g === group ? i : null}
                    editing={true}
                    activeGroup={activeGroup}
                    activeSegment={activeSegment}
                  />
                );
                
              case 'ellipse':
                return (
                  <Ellipse
                    key={key}
                    ellipse={pattern.points}
                    colour={pattern.template?'FF0000':pattern.colour}
                    imageUrl={imageUrl}
                    metadata={metadata[g]}
                    idx={currentSegment === index && g === group ? i : null}
                    editing={true}
                    activeGroup={activeGroup}
                    activeSegment={activeSegment}
                  />
                );
                
              case 'lines':
                return (
                  <Line
                    key={key}
                    squareSize={960}
                    points={pattern.points}
                    colour={pattern.template?'FF0000':pattern.colour}
                    imageUrl={imageUrl}
                    metadata={metadata[g]}
                    idx={currentSegment === index && g === group ? i : null}
                    editing={true}
                    activeGroup={activeGroup}
                    activeSegment={activeSegment}
                  />
                );
                
              default:
                return null;
            }
          })}
          </>
        )})}
      </div>
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          color: 'red',
          fontWeight: 'bold',
          fontSize: '20px', // Adjust size as needed
        }}
      >
        
      </div>
    </div>
  );
};

export default Magnifier;