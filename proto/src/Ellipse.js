import React, { useState } from 'react';

const Ellipse = ({ ellipse: initialEllipse }) => {
  const [ellipse, setEllipse] = useState(initialEllipse);
  const [isSelected, setIsSelected] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [draggedPointIndex, setDraggedPointIndex] = useState(null);
  const [dragStart, setDragStart] = useState(null);

  function calculateEllipseParameters() {
    // First and last points are vertices on major axis
    const [p1, coVertex, p2] = ellipse;
    
    // Center is midpoint of vertices
    const center = [
      (p1[0] + p2[0]) / 2,
      (p1[1] + p2[1]) / 2
    ];
    
    // Semi-major axis length (a)
    const a = Math.sqrt(
      Math.pow(p2[0] - p1[0], 2) + Math.pow(p2[1] - p1[1], 2)
    ) / 2;
    
    // Angle of rotation (major axis)
    const angle = Math.atan2(p2[1] - p1[1], p2[0] - p1[0]);
    
    // Distance from center to co-vertex
    const coVertexDist = Math.sqrt(
      Math.pow(coVertex[0] - center[0], 2) + 
      Math.pow(coVertex[1] - center[1], 2)
    );
    
    // Semi-minor axis length (b)
    const b = coVertexDist;
    
    return { center, a, b, angle };
  }


  function handleMouseDown(e) {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

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

  function handleMouseMove(e) {
    if (!isDragging) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (draggedPointIndex !== null) {
      // Moving a control point
      const newEllipse = [...ellipse];
      newEllipse[draggedPointIndex] = [x, y];
      setEllipse(newEllipse);
    } else {
      // Moving the entire ellipse
      const dx = x - dragStart[0];
      const dy = y - dragStart[1];

      const newEllipse = ellipse.map(point => [
        point[0] + dx,
        point[1] + dy
      ]);

      setEllipse(newEllipse);
      setDragStart([x, y]);
    }
  }

  function handleMouseUp() {
    setIsDragging(false);
    setDraggedPointIndex(null);
  }

  const { center, a, b, angle } = calculateEllipseParameters();

  return (
    <svg 
      width="400" 
      height="400"
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      style={{ position: 'absolute', top: 0, left: 0, cursor: isDragging ? 'grabbing' : isSelected ? 'grab' : 'default' }}
    >
      <ellipse
        cx={center[0]}
        cy={center[1]}
        rx={a}
        ry={b}
        transform={`rotate(${angle * 180 / Math.PI} ${center[0]} ${center[1]})`}
        fill="none"
        stroke="purple"
        strokeWidth="2"
        pointerEvents="visible"
      />
      {isSelected && ellipse.map((point, index) => (
        <circle
          key={index}
          cx={point[0]}
          cy={point[1]}
          r={index === draggedPointIndex ? 8 : 4}
          fill={index === draggedPointIndex ? 'rgba(255, 0, 255, 0.5)' : 'purple'}
          pointerEvents="visible"
        />
      ))}
    </svg>
  );
};

export default Ellipse;