import React, { useState, useRef, useEffect } from 'react';
import Magnifier from './Magnifier';

const Arc = ({ arc: initialArc, colour, onChange, imageUrl, isLeftSquare, metadata, idx, editing, filter}) => {
  const [arc, setArc] = useState(initialArc);
  const [isSelected, setIsSelected] = useState(idx);
  const [isDragging, setIsDragging] = useState(false);
  const [draggedPointIndex, setDraggedPointIndex] = useState(idx);
  const [dragStart, setDragStart] = useState(null);
  const arcRef = useRef(null);
  const patternColor = colour

  const [showMagnifier, setShowMagnifier] = useState(false);
  const [cursorPosition, setCursorPosition] = useState({ x: 0, y: 0 });

  useEffect(()=>{
    setDraggedPointIndex(idx)
    setIsSelected(idx!=null)
  },[idx])
  
  useEffect(()=>{
    setArc(initialArc)
  },[initialArc])

  // Add effect for document-level event handling
  useEffect(() => {
    const handleGlobalMove = (e) => {
      if (!isDragging) return;

      e.preventDefault();
      const event = e.touches ? e.touches[0] : e;
      const rect = arcRef.current.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      setCursorPosition({ x: x, y: y });

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
  }, [isDragging, draggedPointIndex, dragStart, arc, onChange]);

  // Add effect for click outside handling
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (arcRef.current && !arcRef.current.contains(e.target)) {
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
    const rect = arcRef.current.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    setCursorPosition({ x, y });
  
    const controlPointIndex = arc.findIndex(point => 
      Math.sqrt(Math.pow(x - point[0], 2) + Math.pow(y - point[1], 2)) < 25
    );
    
    if (controlPointIndex !== -1) {
      setIsDragging(true);
      setDraggedPointIndex(controlPointIndex);
      setDragStart([x, y]);
      setIsSelected(true);
      setShowMagnifier(true);
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

  const { center, radius } = findCircle(arc[0], arc[1], arc[2]);
  
  function calculate(arc){
    const x1 = arc[0][0], y1 = arc[0][1];
    const x2 = arc[1][0], y2 = arc[1][1];
    const x3 = arc[2][0], y3 = arc[2][1];

    let sweepFlag = 1;
    let largeArcFlag = 1;
    if (x1 !== x3){
      let k = (y3-y1)/(x3-x1)
      let b = y1 - k * x1
      if((((k < 0 && x1 > x3)||(k > 0 && x1 > x3)) && y2 <= k * x2 + b) || (((k > 0 && x1 < x3) || (k < 0 && x1 < x3)) && y2 >= k * x2 + b)){
        sweepFlag = 0
      }
    }else{
      if((y1 < y3 && x2 < x1) || (y1 > y3 && x2 > x1)) sweepFlag = 0;
    }
    let midx=(x1+x3)/2
    let midy=(y1+y3)/2

    let half=Math.sqrt(
      Math.pow(midx - x1, 2) + Math.pow(midy - y1, 2)
    );
    let p2tomid=Math.sqrt(
      Math.pow(midx - x2, 2) + Math.pow(midy - y2, 2)
    );
    if (p2tomid < half) {
      largeArcFlag=0
    }
    return [largeArcFlag, sweepFlag]
  }
  let param = calculate(arc)
  
  const d = `
    M ${arc[0][0]} ${arc[0][1]}
    A ${radius} ${radius} 0 ${param[0]} ${param[1]} ${arc[2][0]} ${arc[2][1]}
  `;
{// // 
// function getLineEquation(p1, p2) {
//   if (p2[0] - p1[0] === 0) {
//     return { isVertical: true, x: p1[0] };
//   }
//   const k = (p2[1] - p1[1]) / (p2[0] - p1[0]);
//   const b = p1[1] - k * p1[0];
//   return { isVertical: false, k, b };
// }

// function isPointAboveLine(point, lineEquation) {
//   if (lineEquation.isVertical) {
//     // For vertical lines, "above" means to the right
//     return point[0] > lineEquation.x;
//   }
//   const expectedY = lineEquation.k * point[0] + lineEquation.b;
//   return point[1] < expectedY;
// }

// function getMidpoint(p1, p2) {
//   return [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2];
// }

// function getDistance(p1, p2) {
//   return Math.sqrt(Math.pow(p2[0] - p1[0], 2) + Math.pow(p2[1] - p1[1], 2));
// }

// // In your render logic:
// const { center, radius } = findCircle(arc[0], arc[1], arc[2]);
// const lineEquation = getLineEquation(arc[0], arc[2]);
// const isSecondPointAbove = isPointAboveLine(arc[1], lineEquation);

// // Handle the case where points have the same X coordinate
// let isFirstPointRightOfLast;
// if (arc[0][0] === arc[2][0]) {
//   // If vertical line, compare Y coordinates
//   isFirstPointRightOfLast = arc[0][1] > arc[2][1];
// } else {
//   isFirstPointRightOfLast = arc[0][0] > arc[2][0];
// }

// // Calculate midpoint of chord
// const chordMidpoint = getMidpoint(arc[0], arc[2]);

// // Calculate distance from second point to chord midpoint
// const distanceToMidpoint = getDistance(arc[1], chordMidpoint);
// const chordLength = getDistance(arc[0], arc[2]);

// // Use distance to midpoint for largeArcFlag threshold
// const largeArcFlag = distanceToMidpoint > chordLength / 2 ? 1 : 0;

// // For vertical lines, we need to adjust our logic
// let sweepFlag;
// if (lineEquation.isVertical) {
//   // For vertical lines, "above" means to the right of the line
//   sweepFlag = isSecondPointAbove !== isFirstPointRightOfLast ? 1 : 0;
// } else {
//   sweepFlag = isSecondPointAbove !== isFirstPointRightOfLast ? 1 : 0;
// }

// const d = `
//   M ${arc[0][0]} ${arc[0][1]}
//   A ${radius} ${radius} 0 ${largeArcFlag} ${sweepFlag} ${arc[2][0]} ${arc[2][1]}
// `;
// // 
}
  return (
    <>
    <svg 
      ref={arcRef}
      width="960" 
      height="960"
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
          stroke={`#${patternColor}`}
          strokeWidth={editing?"2":"5"}
          strokeDasharray={patternColor==='FF0000'?"5,5":''}
        />
        {(isSelected && arc) && arc.map((point, index) => (
          <circle
            key={index}
            cx={point[0]}
            cy={point[1]}
            r={index === draggedPointIndex ? 20 : 10}
            strokeWidth="2"
            stroke={`#${patternColor}`}
            fill={index === draggedPointIndex ? 'rgba(255, 255, 0, 0)' : `#${patternColor}`}
            onMouseDown={(e) => handleMouseDown(e, index)}
            onTouchStart={(e) => handleMouseDown(e, index)}
          />
        ))}
      </g>
    </svg>
    {/* Magnifier */}
    <Magnifier 
        show={showMagnifier}
        position={cursorPosition}
        imageUrl={imageUrl}
        magnification={2}
        isLeftSquare={isLeftSquare}
        metadata={metadata}
        idx={draggedPointIndex}
        filter={filter}
      />
    </>
  );
};

export default Arc;