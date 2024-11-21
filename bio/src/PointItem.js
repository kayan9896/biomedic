// PointItem.js
import React, { useRef, useEffect } from 'react';

const PointItem = ({ x, y, updateCurves, updateDistances }) => {
  const pointRef = useRef(null);

  useEffect(() => {
    const handleMouseDown = (event) => {
      if (event.button === 0) {
        const startX = event.clientX - x;
        const startY = event.clientY - y;

        const handleMouseMove = (moveEvent) => {
          const newX = moveEvent.clientX - startX;
          const newY = moveEvent.clientY - startY;

          updateCurves((prevCurves) => {
            const updatedCurves = prevCurves.map(curve => 
              curve.map(point => 
                point.x === x && point.y === y 
                  ? { ...point, x: newX, y: newY } 
                  : point
              )
            );
            return updatedCurves;
          });
        };

        const handleMouseUp = () => {
          document.removeEventListener('mousemove', handleMouseMove);
          document.removeEventListener('mouseup', handleMouseUp);
          updateDistances();
        };

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
      }
    };

    const pointElement = pointRef.current;
    pointElement.addEventListener('mousedown', handleMouseDown);

    return () => {
      pointElement.removeEventListener('mousedown', handleMouseDown);
    };
  }, [x, y, updateCurves, updateDistances]);

  return (
    <div
      ref={pointRef}
      className="point-item"
      style={{
        position: 'absolute',
        left: `${x - 5}px`,
        top: `${y - 5}px`,
        width: '10px',
        height: '10px',
        backgroundColor: 'red',
        borderRadius: '50%',
        cursor: 'pointer'
      }}
    />
  );
};

export default PointItem;