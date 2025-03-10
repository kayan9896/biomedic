import React, { useState, useEffect, useRef } from 'react';
import Magnifier from './Magnifier';

const Circle = ({ center:ori, edgePoint:edge, onCenterChange, onEdgePointChange, imageUrl }) => {
  const [center,setcCenter]=useState(ori)
  const [edgePoint,setEdgePoint]=useState(edge)
  const [isDraggingCenter, setIsDraggingCenter] = useState(false);
  const [isDraggingEdge, setIsDraggingEdge] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const svgRef = useRef(null);

  const [showMagnifier, setShowMagnifier] = useState(false);
  const [cursorPosition, setCursorPosition] = useState({ x: 0, y: 0 });
  // Point styles
  const normalPointStyle = {
    r: 10,
    fill: 'blue',
    strokeWidth: 0
  };

  const draggedPointStyle = {
    r: 20,
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
    setShowMagnifier(true)
  };

  const handleCircleClick = (e) => {
    e.stopPropagation();
    if (!isEditing) {
      setIsEditing(true);
    }
  };

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (svgRef.current && !svgRef.current.contains(e.target)) {
        setIsEditing(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    //document.addEventListener('touchstart', handleClickOutside);
    
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      //document.removeEventListener('touchstart', handleClickOutside);
    };
  }, []);

  
  useEffect(() => {
    const handleGlobalMove = (e) => {
      if (isDraggingCenter || isDraggingEdge) {
        e.preventDefault();
        const event = e.touches ? e.touches[0] : e;
        const svgRect = svgRef.current.getBoundingClientRect();
        const x = event.clientX - svgRect.left;
        const y = event.clientY - svgRect.top;
        setCursorPosition({ x: x, y: y });
  
        if (isDraggingCenter) {
          // Handle center dragging
          const dx = x - center[0];
          const dy = y - center[1];
          setcCenter([x, y]);
          onCenterChange([x, y]);
          onEdgePointChange([edgePoint[0] + dx, edgePoint[1] + dy]);
          setEdgePoint([edgePoint[0] + dx, edgePoint[1] + dy]);
        } else if (isDraggingEdge) {
          // Handle edge dragging
          onEdgePointChange([x, y]);
          setEdgePoint([x, y]);
        }
      }
    };
  
    const handleGlobalUp = () => {
      setIsDraggingCenter(false);
      setIsDraggingEdge(false);
      setShowMagnifier(false)
    };
  
    if (isDraggingCenter || isDraggingEdge) {
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
  }, [isDraggingCenter, isDraggingEdge, center, edgePoint]);

  return (
    <>
    <svg 
      ref={svgRef}
      width="960px" 
      height="960px" 
      pointerEvents="none"
      style={{ position: 'absolute', top: 0, left: 0,cursor: isDraggingCenter || isDraggingEdge ? 'grabbing' : 'default' }}
    >
      <g >
        {/* Circle */}
        <circle
          cx={center[0]}
          cy={center[1]}
          r={calculateRadius()}
          fill="none"
          stroke="transparent"
          strokeWidth="20"
          pointerEvents="auto"
          style={{ cursor: 'pointer' }}
          onMouseDown={handleCircleClick}
          onTouchStart={handleCircleClick}
        />

        <circle
          cx={center[0]}
          cy={center[1]}
          r={calculateRadius()}
          fill="none"
          stroke="blue"
          strokeWidth="2"
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
              onTouchStart={(e) => handleMouseDown(e, false)}
              {...(isDraggingEdge ? draggedPointStyle : normalPointStyle)}
            />
          </>
        )}
      </g>
    </svg>
    <Magnifier 
      show={showMagnifier}
      position={cursorPosition}
      imageUrl={imageUrl}
      magnification={2}
      size={150}
    />
    </>
  );
};

export default Circle;