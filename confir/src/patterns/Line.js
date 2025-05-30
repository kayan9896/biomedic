import React, { useState, useRef, useEffect } from 'react';
import Magnifier from './Magnifier'; 
import * as THREE from 'three';

const Line = ({ squareSize, points, colour, onChange, imageUrl, metadata, isLeftSquare, idx, editing }) => {
  const [curvePoints, setCurvePoints] = useState(points);
  const [showDots, setShowDots] = useState(idx);
  const [activeDotIndex, setActiveDotIndex] = useState(idx);
  const [isMouseDown, setIsMouseDown] = useState(false);
  const [dragLine, setDragLine] = useState(false);
  const [cursorPosition, setCursorPosition] = useState({ x: 0, y: 0 });
  const lineRef = useRef(null);
  const patternColor = colour

  const HIT_TOLERANCE = 15;
  useEffect(()=>{
    setActiveDotIndex(idx)
    setShowDots(idx!==null)
    },[idx])

  useEffect(() => {
    setCurvePoints(points);
    }, [points]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (lineRef.current && !lineRef.current.contains(e.target)) {
        setShowDots(false);
        setActiveDotIndex(null);
      }
    };
  
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  

  useEffect(() => {
    const handleGlobalMove = (e) => {
      if (!isMouseDown) return;
  
      const rect = lineRef.current.getBoundingClientRect();
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;
      const x = clientX - rect.left;
      const y = clientY - rect.top;
      
      // Update cursor position for magnifier
      setCursorPosition({ x, y });
  
      const controlPointIndex = curvePoints.findIndex(point => 
        Math.sqrt(Math.pow(x - point[0], 2) + Math.pow(y - point[1], 2)) < 25
      );
      
      if (controlPointIndex !== -1) {
        const newPoints = [...curvePoints];
        newPoints[activeDotIndex] = [x, y];
        setCurvePoints(newPoints);
        if (onChange) {
          onChange(newPoints);
        }
      } else if (dragLine) {
        const dx = x - dragLine.startX;
        const dy = y - dragLine.startY;
        
        const newPoints = dragLine.originalPoints.map(point => [
          point[0] + dx,
          point[1] + dy
        ]);
        setActiveDotIndex(null)
        setCurvePoints(newPoints);
        if (onChange) {
          onChange(newPoints);
        }
      }
    };
  
    const handleGlobalEnd = () => {
      
      setDragLine(false);
      setIsMouseDown(false);
    };
  
    window.addEventListener('mousemove', handleGlobalMove);
    window.addEventListener('mouseup', handleGlobalEnd);
    window.addEventListener('touchmove', handleGlobalMove, { passive: false });
    window.addEventListener('touchend', handleGlobalEnd);
  
    return () => {
      window.removeEventListener('mousemove', handleGlobalMove);
      window.removeEventListener('mouseup', handleGlobalEnd);
      window.removeEventListener('touchmove', handleGlobalMove);
      window.removeEventListener('touchend', handleGlobalEnd);
    };
  }, [isMouseDown, activeDotIndex, dragLine, curvePoints, squareSize]);

  const handleDotMouseDown = (e, index) => {
    e.preventDefault();
    e.stopPropagation();
    
    const rect = lineRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setCursorPosition({ x, y });
    
    setActiveDotIndex(index);
    setIsMouseDown(true);
    setShowDots(true);
  };

  const handleLineMouseDown = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const rect = lineRef.current.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    setCursorPosition({ x: mouseX, y: mouseY });
    
    setDragLine({
      startX: mouseX,
      startY: mouseY,
      originalPoints: [...curvePoints]
    });
    setIsMouseDown(true);
    setShowDots(true);
  };

  const handleTouchStart = (e) => {
    e.preventDefault();
    const touch = e.touches[0];
    const rect = lineRef.current.getBoundingClientRect();
    const touchX = touch.clientX - rect.left;
    const touchY = touch.clientY - rect.top;

    setCursorPosition({ x: touchX, y: touchY });
    
    setDragLine({
      startX: touchX,
      startY: touchY,
      originalPoints: [...curvePoints]
    });
    setIsMouseDown(true);
    setShowDots(true);
  };

  const handleDotTouchStart = (e, index) => {
    e.preventDefault();
    e.stopPropagation();
    
    const rect = lineRef.current.getBoundingClientRect();
    const touch = e.touches[0];
    const x = touch.clientX - rect.left;
    const y = touch.clientY - rect.top;
    setCursorPosition({ x, y });
    
    setActiveDotIndex(index);
    setIsMouseDown(true);
    setShowDots(true);
  };

  
 
  const createSmoothPath = (points) => {
    // Convert points to THREE.Vector2
    const vectors = points.map(p => new THREE.Vector2(p[0], p[1]));
    
    // Create a curve
    const curve = new THREE.SplineCurve(vectors);
    
    // Get points along the curve
    const curvePoints = curve.getPoints(50); // 50 divisions
    
    // Convert to SVG path
    let path = `M${curvePoints[0].x},${curvePoints[0].y}`;
    curvePoints.slice(1).forEach(p => {
      path += ` L${p.x},${p.y}`;
    });
    
    return path;
  };

  // Generate the smooth path using D3
  const pathCommand = createSmoothPath(curvePoints);


  // Show magnifier only when a dot is being dragged
  const showMagnifier = isMouseDown && activeDotIndex !== null;

  return (
    <>
      <svg 
        ref={lineRef}
        width={squareSize} 
        height={squareSize}
        style={{ position: 'absolute', top: 0, left: 0 }}
        pointerEvents="none"
      >
        {/* Invisible path for hit detection */}
        <path
          d={pathCommand}
          stroke="transparent"
          strokeWidth={HIT_TOLERANCE * 2}
          fill="none"
          style={{ cursor: 'move' }}
          pointerEvents="auto"
          onMouseDown={handleLineMouseDown}
          onTouchStart={handleTouchStart}
        />
        {/* Visible smooth curve */}
        <path
          d={pathCommand}
          stroke={`#${patternColor}`}
          strokeWidth={editing?"2":"5"}
          strokeDasharray={patternColor==='FF0000'?"5,5":''}
          fill="none"
          pointerEvents="none"
        />
      </svg>

      {(points.length === 1 || showDots) && curvePoints.map((point, index) => (
        <div
          key={index}
          className="draggable-dot"
          style={{
            width: activeDotIndex === index ? '40px' : '20px',
            height: activeDotIndex === index ? '40px' : '20px',
            backgroundColor: activeDotIndex === index ? 'transparent' : `#${patternColor}`,
            border: `2px solid #${patternColor}`,
            borderRadius: '50%',
            position: 'absolute',
            cursor: 'move',
            left: `${point[0]-2 - (activeDotIndex === index ? 20 : 10)}px`,
            top: `${point[1]-2 - (activeDotIndex === index ? 20 : 10)}px`,
            touchAction: 'none',
            pointerEvents: "auto",
            zIndex: 10
          }}
          onMouseDown={(e) => handleDotMouseDown(e, index)}
          onTouchStart={(e) => handleDotTouchStart(e, index)}
        />
      ))}

      {/* Magnifier */}
      <Magnifier 
        show={showMagnifier}
        position={cursorPosition}
        imageUrl={imageUrl}
        magnification={2}
        isLeftSquare={isLeftSquare}
        metadata={metadata}
        idx={activeDotIndex}
      />
    </>
  );
};

export default Line;
