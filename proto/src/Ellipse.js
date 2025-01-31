import React, { useState, useRef, useEffect } from 'react';

const Ellipse = ({ ellipse: initialEllipse, onChange }) => {
  const [ellipse, setEllipse] = useState(initialEllipse);
  const [isSelected, setIsSelected] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [draggedPointIndex, setDraggedPointIndex] = useState(null);
  const [dragStart, setDragStart] = useState(null);
  const ellipseRef = useRef(null);

  // Add effect for document-level event handling
  useEffect(() => {
    const handleGlobalMove = (e) => {
      if (!isDragging) return;
      
      e.preventDefault();
      const event = e.touches ? e.touches[0] : e;
      const rect = ellipseRef.current.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;

      if (draggedPointIndex !== null) {
        // Moving a control point
        const newEllipse = [...ellipse];
        newEllipse[draggedPointIndex] = [x, y];
        setEllipse(newEllipse);
        if (onChange) {
          onChange(newEllipse);
        }
      } else {
        // Moving the entire ellipse
        const dx = x - dragStart[0];
        const dy = y - dragStart[1];

        const newEllipse = ellipse.map(point => [
          point[0] + dx,
          point[1] + dy
        ]);

        setEllipse(newEllipse);
        if (onChange) {
          onChange(newEllipse);
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
  }, [isDragging, draggedPointIndex, dragStart, ellipse, onChange]);

  // Add effect for click outside handling
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (ellipseRef.current && !ellipseRef.current.contains(e.target)) {
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
    const rect = ellipseRef.current.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    const controlPointIndex = ellipse.findIndex(point => 
      Math.sqrt(Math.pow(x - point[0], 2) + Math.pow(y - point[1], 2)) < 5
    );
    
    if (controlPointIndex !== -1) {
      setIsDragging(true);
      setDraggedPointIndex(controlPointIndex);
      setDragStart([x, y]);
      setIsSelected(true);
    } else if (e.target.tagName === 'ellipse') {
      setIsDragging(true);
      setDraggedPointIndex(null);
      setDragStart([x, y]);
      setIsSelected(true);
    } else {
      setIsSelected(false);
    }
  }

  function calculateEllipseParameters() {
    const [p1, coVertex, p2] = ellipse;
    
    const center = [
      (p1[0] + p2[0]) / 2,
      (p1[1] + p2[1]) / 2
    ];
    
    const a = Math.sqrt(
      Math.pow(p2[0] - p1[0], 2) + Math.pow(p2[1] - p1[1], 2)
    ) / 2;
    
    const angle = Math.atan2(p2[1] - p1[1], p2[0] - p1[0]);
    
    const coVertexDist = Math.sqrt(
      Math.pow(coVertex[0] - center[0], 2) + 
      Math.pow(coVertex[1] - center[1], 2)
    );
    
    const b = coVertexDist;
    
    return { center, a, b, angle };
  }

  const { center, a, b, angle } = calculateEllipseParameters();

  return (
    <svg 
      ref={ellipseRef}
      width="400" 
      height="400"
      onMouseDown={handleMouseDown}
      onTouchStart={handleMouseDown}
      style={{ position: 'absolute', top: 0, left: 0, cursor: isDragging ? 'grabbing' : isSelected ? 'grab' : 'default' }}
      pointerEvents="none"
    >
      <g pointerEvents="auto">
        <ellipse
          cx={center[0]}
          cy={center[1]}
          rx={a}
          ry={b}
          transform={`rotate(${angle * 180 / Math.PI} ${center[0]} ${center[1]})`}
          fill="none"
          stroke="transparent"
          strokeWidth="20"
          style={{ cursor: 'pointer' }}
        />
        <ellipse
          cx={center[0]}
          cy={center[1]}
          rx={a}
          ry={b}
          transform={`rotate(${angle * 180 / Math.PI} ${center[0]} ${center[1]})`}
          fill="none"
          stroke="purple"
          strokeWidth="2"
        />
        {isSelected && ellipse.map((point, index) => (
          <circle
            key={index}
            cx={point[0]}
            cy={point[1]}
            r={index === draggedPointIndex ? 8 : 4}
            fill={index === draggedPointIndex ? 'rgba(255, 0, 255, 0.5)' : 'purple'}
          />
        ))}
      </g>
    </svg>
  );
};

export default Ellipse;