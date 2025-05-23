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
      Math.sqrt(Math.pow(x - point[0], 2) + Math.pow(y - point[1], 2)) < 30
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
    const [p1, p3, p2] = ellipse;
    
    // Calculate center as midpoint of p1 and p2
    const center = [
      (p1[0] + p2[0]) / 2,
      (p1[1] + p2[1]) / 2
    ];
    
    // Calculate rotation angle
    const angle = Math.atan2(p2[1] - p1[1], p2[0] - p1[0]);
    
    // Transform points to align major axis with x-axis
    const cosAngle = Math.cos(-angle);
    const sinAngle = Math.sin(-angle);
    
    function rotatePoint(p) {
      const dx = p[0] - center[0];
      const dy = p[1] - center[1];
      return [
        dx * cosAngle - dy * sinAngle + center[0],
        dx * sinAngle + dy * cosAngle + center[1]
      ];
    }
    
    const [rp1, rp3, rp2] = [p1, p3, p2].map(rotatePoint);
    
    // Calculate semi-major axis (a)
    const a = Math.sqrt(
      Math.pow(p2[0] - p1[0], 2) + Math.pow(p2[1] - p1[1], 2)
    ) / 2;
    
    // Transform p3 coordinates relative to center and rotated
    const x = rp3[0] - center[0];
    const y = rp3[1] - center[1];
    
    // Using the ellipse equation (x²/a² + y²/b² = 1), solve for b
    // We know this point lies on the ellipse, so:
    const b = Math.abs(y) * a / Math.sqrt(a * a - x * x);
    
    return { center, a, b, angle };
  }

  const { center, a, b, angle } = calculateEllipseParameters();

  return (
    <svg 
      ref={ellipseRef}
      width="700" 
      height="700"
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
          <>
          <circle
            key={index}
            cx={point[0]}
            cy={point[1]}
            r={index === draggedPointIndex ? 20 : 10}
            fill={index === draggedPointIndex ? 'rgba(255, 0, 255, 0.5)' : 'purple'}
          />
          <circle
            key={index}
            cx={point[0]}
            cy={point[1]}
            r={index === draggedPointIndex ? 40 : 20}
            fill='transparent'
          />
          </>
        ))}
      </g>
    </svg>
  );
};

export default Ellipse;