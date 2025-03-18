import React, { useRef, useEffect } from 'react';
import Circle from './Circle';
import Arc from './Arc';
import Ellipse from './Ellipse';
import Line from './Line';

const Magnifier = ({ 
  show, 
  imageUrl, 
  magnification = 2,
  size = 150,
  position: { x, y } ,
  metadata
}) => {
  const magnificationLevel = 2;
  const magnifierSize = 150;
  if (!show) return null;

  return (
    <div 
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
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
      <div style={{position:'absolute', top: 0, left:0}}>+</div>
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
            <img src={imageUrl} alt="Image 1" style={{ width: '100%', height: 'auto' }} />
        
            {metadata.map((pattern, index) => {
            const key = `${pattern.type}-${index}`;
            
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
                    
                    imageUrl={imageUrl}
                    metadata={metadata}
                  />
                );
                
              case 'ellipse':
                return (
                  <Ellipse
                    key={key}
                    ellipse={pattern.points}
                    
                    imageUrl={imageUrl}
                    metadata={metadata}
                  />
                );
                
              case 'lines':
                return (
                  <Line
                    key={key}
                    squareSize={960}
                    points={pattern.points}
                    
                    imageUrl={imageUrl}
                    metadata={metadata}
                  />
                );
                
              default:
                return null;
            }
          })}
      </div>
    </div>
  );
};

export default Magnifier;