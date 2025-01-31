import React, { useState, useRef, useEffect } from 'react';

const Arc = ({ arc: initialArc, onChange }) => {
  const [arc, setArc] = useState(initialArc);
  const [isSelected, setIsSelected] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [draggedPointIndex, setDraggedPointIndex] = useState(null);
  const [dragStart, setDragStart] = useState(null);
  const arcRef = useRef(null);

  // Add effect for document-level event handling
  useEffect(() => {
    const handleGlobalMove = (e) => {
      if (!isDragging) return;

      e.preventDefault();
      const event = e.touches ? e.touches[0] : e;
      const rect = arcRef.current.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;

      if (draggedPointIndex !== null) {
        // Moving a control point
        const newArc = [...arc];
        newArc[draggedPointIndex] = [x, y];
        setArc(newArc);
        if (onChange) {
          onChange(newArc);
        }
      } else {
        // Moving the entire arc
        const dx = x - dragStart[0];
        const dy = y - dragStart[1];

        const newArc = arc.map(point => [
          point[0] + dx,
          point[1] + dy
        ]);

        setArc(newArc);
        if (onChange) {
          onChange(newArc);
        }
        setDragStart([x, y]);
      }
    };

    const handleGlobalUp = () => {
      setIsDragging(false);
      setDraggedPointIndex(null);
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
  }, [isDragging, draggedPointIndex, dragStart, arc, onChange]);

  // Add effect for click outside handling
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (arcRef.current && !arcRef.current.contains(e.target)) {
        setIsSelected(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  function handleMouseDown(e) {
    e.preventDefault();
    e.stopPropagation();

    const event = e.touches ? e.touches[0] : e;
    const rect = arcRef.current.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    const controlPointIndex = arc.findIndex(point => 
      Math.sqrt(Math.pow(x - point[0], 2) + Math.pow(y - point[1], 2)) < 5
    );
    
    if (controlPointIndex !== -1) {
      setIsDragging(true);
      setDraggedPointIndex(controlPointIndex);
      setDragStart([x, y]);
      setIsSelected(true);
    } else if (e.target.tagName === 'path') {
      setIsDragging(true);
      setDraggedPointIndex(null);
      setDragStart([x, y]);
      setIsSelected(true);
    } else {
      setIsSelected(false);
    }
  }

  function findCircle(p1, p2, p3) {
    const x1 = p1[0], y1 = p1[1];
    const x2 = p2[0], y2 = p2[1];
    const x3 = p3[0], y3 = p3[1];
    
    const a = x1 * (y2 - y3) - y1 * (x2 - x3) + x2 * y3 - x3 * y2;
    const b = (x1 * x1 + y1 * y1) * (y3 - y2) + 
              (x2 * x2 + y2 * y2) * (y1 - y3) + 
              (x3 * x3 + y3 * y3) * (y2 - y1);
    const c = (x1 * x1 + y1 * y1) * (x2 - x3) + 
              (x2 * x2 + y2 * y2) * (x3 - x1) + 
              (x3 * x3 + y3 * y3) * (x1 - x2);
    
    const x = -b / (2 * a);
    const y = -c / (2 * a);
    
    const radius = Math.sqrt(
      Math.pow(x - x1, 2) + Math.pow(y - y1, 2)
    );
    
    return { center: [x, y], radius };
  }

  function calculateAngle(center, point) {
    return Math.atan2(point[1] - center[1], point[0] - center[0]);
  }

  const { center, radius } = findCircle(arc[0], arc[1], arc[2]);
  let startAngle = calculateAngle(center, arc[0]);
  let midAngle = calculateAngle(center, arc[1]);
  let endAngle = calculateAngle(center, arc[2]);

  while (midAngle < startAngle) midAngle += 2 * Math.PI;
  while (endAngle < midAngle) endAngle += 2 * Math.PI;

  const longWay = endAngle - startAngle > Math.PI;

  if (longWay) {
    [startAngle, endAngle] = [endAngle, startAngle];
  }

  const sweepFlag = longWay ? 0 : 1;
  const largeArcFlag = longWay ? 1 : 0;

  const d = `
    M ${arc[0][0]} ${arc[0][1]}
    A ${radius} ${radius} 0 ${largeArcFlag} ${sweepFlag} ${arc[2][0]} ${arc[2][1]}
  `;

  return (
    <svg 
      ref={arcRef}
      width="400" 
      height="400"
      style={{ 
        position: 'absolute', 
        top: 0, 
        left: 0, 
        cursor: isDragging ? 'grabbing' : isSelected ? 'grab' : 'default'
      }}
      pointerEvents="none"
    >
      <g pointerEvents="auto">
        <path
          d={d}
          fill="none"
          stroke="transparent"
          strokeWidth="20"
          onMouseDown={handleMouseDown}
          onTouchStart={handleMouseDown}
          style={{ cursor: 'pointer' }}
        />
        <path
          d={d}
          fill="none"
          stroke="yellow"
          strokeWidth="2"
        />
        {isSelected && arc.map((point, index) => (
          <circle
            key={index}
            cx={point[0]}
            cy={point[1]}
            r={index === draggedPointIndex ? 20 : 10}
            strokeWidth="20"
            fill={index === draggedPointIndex ? 'rgba(255, 255, 0, 0.5)' : 'yellow'}
            onMouseDown={(e) => handleMouseDown(e, index)}
            onTouchStart={(e) => handleMouseDown(e, index)}
          />
        ))}
      </g>
    </svg>
  );
};

export default Arc;