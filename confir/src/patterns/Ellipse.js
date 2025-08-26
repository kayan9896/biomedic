import React, { useState, useRef, useEffect } from 'react';
import Arc from './Arc';
import Magnifier from './Magnifier';

const Ellipse = ({ segment, group, ellipse: initialEllipse, colour, onChange, groupOffset, imageUrl, isLeftSquare, metadata, fulldata, idx, editing, filter, activeGroup, activeSegment, setActiveGroupSegment}) => {
  const [ellipse, setEllipse] = useState(initialEllipse);
  const [isSelected, setIsSelected] = useState(idx!==null);
  const [isDragging, setIsDragging] = useState(false);
  const [draggedPointIndex, setDraggedPointIndex] = useState(idx);
  const [dragStart, setDragStart] = useState(null);
  const ellipseRef = useRef(null);
  const [arcPoints, setArcPoints] = useState([initialEllipse[0], initialEllipse[3], initialEllipse[2]]);
  const [showMagnifier, setShowMagnifier] = useState(false);
  const [cursorPosition, setCursorPosition] = useState({ x: 0, y: 0 });
  const patternColor = colour
  
  useEffect(()=>{
    if(group !== null && segment !== null && (activeGroup !== group || activeSegment !== segment)){
      setIsSelected(false);
      return
    }
    setIsSelected(true)
    },[activeGroup, activeSegment])

  useEffect(()=>{
    setDraggedPointIndex(idx)
    setIsSelected(idx!==null)
  },[idx])
  
  useEffect(()=>{
      setEllipse(initialEllipse)
      setArcPoints([initialEllipse[0], initialEllipse[3], initialEllipse[2]]);
    },[initialEllipse])

  useEffect(() => {
    if (groupOffset) {
      const newEllipse = ellipse.map(point => [
        point[0] + groupOffset[0],
        point[1] + groupOffset[1]
      ]);
      setEllipse(newEllipse);
      if (onChange) {
        onChange(newEllipse);
      }
    }
  }, [groupOffset]);


  // Add effect for document-level event handling
  useEffect(() => {
    const handleGlobalMove = (e) => {
      if (!isDragging) return;
      
      e.preventDefault();
      const event = e.touches ? e.touches[0] : e;
      const rect = ellipseRef.current.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      setCursorPosition({ x: x, y: y });

      if (draggedPointIndex !== null) {
        // Moving a control point
        const newEllipse = [...ellipse];
        newEllipse[draggedPointIndex] = [x, y];
        if(invalid(newEllipse)) return
        if (draggedPointIndex === 0 || draggedPointIndex === 2) {
          const newArc = [...arcPoints];
          newArc[draggedPointIndex] = [x, y];
          setArcPoints(newArc);
        }
    
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
    
        const newArc = arcPoints.map(point => [
          point[0] + dx,
          point[1] + dy
        ]);
    
        setEllipse(newEllipse);
        setArcPoints(newArc);
        if (onChange) {
          onChange(newEllipse);
        }
        setDragStart([x, y]);
      }
    };

    const handleGlobalUp = () => {
      setIsDragging(false);
      
      setShowMagnifier(false)
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
        setDraggedPointIndex(null);
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
    
    setCursorPosition({ x: event.clientX - rect.left, y: event.clientY - rect.top });
    
    const controlPointIndex = ellipse.findIndex(point => 
      Math.sqrt(Math.pow(x - point[0], 2) + Math.pow(y - point[1], 2)) < 30
    );
    
    if (controlPointIndex !== -1) {
      setIsDragging(true);
      setDraggedPointIndex(controlPointIndex);
      setDragStart([x, y]);
      setIsSelected(true);
      setShowMagnifier(true);
    } else if (e.target.tagName === 'ellipse') {
      setIsDragging(true);
      setDraggedPointIndex(null);
      setDragStart([x, y]);
      setIsSelected(true);
    } else {
      setIsSelected(false);
    }
    setActiveGroupSegment(group, segment)
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

  function invalid(newarc) {
    const o = [(newarc[0][0] + newarc[2][0]) / 2, (newarc[0][1] + newarc[2][1]) / 2]
    const r = Math.sqrt(Math.pow(o[0] - newarc[0][0], 2) + Math.pow(o[1] - newarc[0][1], 2))
    return Math.sqrt(Math.pow(o[0] - newarc[1][0], 2) + Math.pow(o[1] - newarc[1][1], 2)) > r || Math.sqrt(Math.pow(o[0] - newarc[3][0], 2) + Math.pow(o[1] - newarc[3][1], 2)) > r
  }

  return (
    <>
    <Arc
      segment={segment}
      group={group}
      arc={[ellipse[0], ellipse[3], ellipse[2], ellipse[1]]}
      onChange={(newArc) => {
        // Update the ellipse points based on the new arc points
        const newEllipse = [newArc[0], newArc[3], newArc[2], newArc[1]];
        setEllipse(newEllipse);
        if (onChange) {
          onChange(newEllipse);
        }
      }}
      colour={colour}
      imageUrl={imageUrl}
      editing={editing}
      ellipseSelect={setIsSelected}
      activeGroup={activeGroup}
      activeSegment={activeSegment}
      setActiveGroupSegment={setActiveGroupSegment}
    />
    <svg 
      ref={ellipseRef}
      width="960" 
      height="960"
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
          stroke={`#${patternColor}`}
          strokeWidth={editing?"2":"5"}
          strokeDasharray={patternColor==='FF0000'?"5,5":''}
        />
        {isSelected && ellipse.map((point, index) => (
          <>
          <circle
            key={index}
            cx={point[0]}
            cy={point[1]}
            r={index === draggedPointIndex ? 20 : 10}
            stroke={`#${patternColor}`}
            strokeWidth={2}
            fill={index === draggedPointIndex ? 'rgba(255, 0, 255, 0)' : `#${patternColor}`}
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
    {/* Magnifier */}
    <Magnifier 
        segment={segment}
        group={group}
        show={showMagnifier}
        position={cursorPosition}
        imageUrl={imageUrl}
        magnification={2}
        isLeftSquare={isLeftSquare}
        metadata={fulldata}
        idx={draggedPointIndex}
        filter={filter}
        activeGroup={activeGroup}
        activeSegment={activeSegment}
      />
    </>
  );
};

export default Ellipse;