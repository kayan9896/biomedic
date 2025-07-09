import React, { useRef, useEffect, useState } from 'react';
import Circle from './Circle';
import Arc from './Arc';
import Ellipse from './Ellipse';
import Line from './Line';

const Magnifier = ({ 
  show, 
  imageUrl, 
  magnification = 2,
  size = 380,
  position: { x, y } ,
  metadata,
  isLeftSquare,
  idx,
  filter
}) => {
    const [magnifierPosition, setMagnifierPosition] = useState('');
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
  
    // Get current coordinates
    const coordinates = getMagnifierCoordinates();
    
    // Check distance between cursor and magnifier
    useEffect(() => {
      if (!show) return;
      
      // Calculate center of magnifier
      const magnifierCenterX = isLeftSquare? size/2 : 960-size/2;
      const magnifierCenterY =  size/2;
      
      // Calculate distance between cursor and magnifier center
      const distance = Math.sqrt(
        Math.pow(magnifierCenterX - x, 2) + 
        Math.pow(magnifierCenterY - y, 2)
      );
      
      // Switch position if cursor is too close
      if (distance < proximityThreshold) {
        setMagnifierPosition('alternate');
      } else {
        setMagnifierPosition('default');
      }
    }, [x, y, show]);

  const magnificationLevel = 2;
  const magnifierSize = size;
  const [i,seti] =useState(idx)
  useEffect(()=>{
    seti(idx)
  },[idx])
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
        
            {metadata&&metadata.map((pattern, index) => {
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
                    colour={pattern.colour}
                    imageUrl={imageUrl}
                    metadata={metadata}
                    idx={i}
                    editing={true}
                  />
                );
                
              case 'ellipse':
                return (
                  <Ellipse
                    key={key}
                    ellipse={pattern.points}
                    colour={pattern.colour}
                    imageUrl={imageUrl}
                    metadata={metadata}
                    idx={i}
                    editing={true}
                  />
                );
                
              case 'lines':
                return (
                  <Line
                    key={key}
                    squareSize={960}
                    points={pattern.points}
                    colour={pattern.colour}
                    imageUrl={imageUrl}
                    metadata={metadata}
                    idx={i}
                    editing={true}
                  />
                );
                
              default:
                return null;
            }
          })}
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
        +
      </div>
    </div>
  );
};

export default Magnifier;