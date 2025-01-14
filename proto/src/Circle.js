import React, { useState, useEffect, useRef } from 'react';

const Circle = ({ center:ori, edgePoint:edge, onCenterChange, onEdgePointChange }) => {
  const [center,setcCenter]=useState(ori)
  const [edgePoint,setEdgePoint]=useState(edge)
  const [isDraggingCenter, setIsDraggingCenter] = useState(false);
  const [isDraggingEdge, setIsDraggingEdge] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const svgRef = useRef(null);

  // Point styles
  const normalPointStyle = {
    r: 5,
    fill: 'blue',
    strokeWidth: 0
  };

  const draggedPointStyle = {
    r: 10,
    fill: 'rgba(0, 0, 255, 0.3)',
    stroke: 'blue',
    strokeWidth: 2
  };

  // Calculate radius
  const calculateRadius = () => {
    return Math.sqrt(
      Math.pow(edgePoint[0] - center[0], 2) + 
      Math.pow(edgePoint[1] - center[1], 2)
    );
  };

  // Handle mouse events
  const handleMouseDown = (e, isCenter) => {
    e.stopPropagation();
    if (isCenter) {
      setIsDraggingCenter(true);
    } else {
      setIsDraggingEdge(true);
    }
  };

  const handleMouseMove = (e) => {
    if (!isDraggingCenter && !isDraggingEdge) return;

    const event = e.touches ? e.touches[0] : e;
    const svgRect = svgRef.current.getBoundingClientRect();
    const x = event.clientX - svgRect.left;
    const y = event.clientY - svgRect.top;

    if (isDraggingCenter) {
      const dx = x - center[0];
      const dy = y - center[1];
      setcCenter([x, y])
      onCenterChange([x, y]);
      onEdgePointChange([edgePoint[0] + dx, edgePoint[1] + dy]);
      setEdgePoint([edgePoint[0] + dx, edgePoint[1] + dy])
    } else if (isDraggingEdge) {
      onEdgePointChange([x, y]);
      setEdgePoint([x, y])
    }
  };

  const handleMouseUp = () => {
    setIsDraggingCenter(false);
    setIsDraggingEdge(false);
  };

  const handleCircleClick = (e) => {
    e.stopPropagation();
    if (!isEditing) {
      setIsEditing(true);
    }
  };

  const handleSvgClick = () => {
    setIsEditing(false);
  };

  useEffect(() => {
    document.addEventListener('mouseup', handleMouseUp);
    return () => {
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

  return (
    <svg 
      ref={svgRef}
      width="100%" 
      height="100%" 
      onMouseMove={handleMouseMove}
      onClick={handleSvgClick}
      pointerEvents="none"
      style={{ position: 'absolute', top: 0, left: 0,cursor: isDraggingCenter || isDraggingEdge ? 'grabbing' : 'default' }}
    >
      <g onClick={handleCircleClick}>
        {/* Circle */}
        <circle
          cx={center[0]}
          cy={center[1]}
          r={calculateRadius()}
          fill="none"
          stroke="blue"
          strokeWidth="2"
          pointerEvents="auto"
          style={{ cursor: 'pointer' }}
        />
        
        {isEditing && (
          <>
            {/* Center point */}
            <circle
              cx={center[0]}
              cy={center[1]}
              cursor="grab"
              pointerEvents="auto"
              onMouseDown={(e) => handleMouseDown(e, true)}
              onTouchStart={(e) => handleMouseDown(e, true)}
              {...(isDraggingCenter ? draggedPointStyle : normalPointStyle)}
            />
            
            {/* Edge point */}
            <circle
              cx={edgePoint[0]}
              cy={edgePoint[1]}
              cursor="grab"
              pointerEvents="auto"
              onMouseDown={(e) => handleMouseDown(e, false)}
              onTouchStart={(e) => handleMouseDown(e, true)}
              {...(isDraggingEdge ? draggedPointStyle : normalPointStyle)}
            />
          </>
        )}
      </g>
    </svg>
  );
};

export default Circle;