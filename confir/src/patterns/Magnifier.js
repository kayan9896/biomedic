import React, { useRef, useEffect, useState } from 'react';
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
  metadata,
  idx
}) => {
  const magnificationLevel = 2;
  const magnifierSize = 150;
  const [i,seti] =useState(idx)
  useEffect(()=>{
    seti(idx)
  },[idx])
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
                    
                    imageUrl={imageUrl}
                    metadata={metadata}
                    idx={i}
                  />
                );
                
              case 'ellipse':
                return (
                  <Ellipse
                    key={key}
                    ellipse={pattern.points}
                    
                    imageUrl={imageUrl}
                    metadata={metadata}
                    idx={i}
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
                    idx={i}
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