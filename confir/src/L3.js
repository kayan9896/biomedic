import React, { useState, useEffect, useRef } from 'react';
import PatternDisplay from './PatternDisplay';

function L3({leftImage, activeLeft, leftImageMetadata, rightImage, activeRight, rightImageMetadata, onSaveLeft, onSaveRight}) {
  const [showMagnifier, setShowMagnifier] = useState(false);
  const [magnifierPosition, setMagnifierPosition] = useState({ x: 0, y: 0 });
  const [cursorPosition, setCursorPosition] = useState({ x: 0, y: 0 });
  const [activeImageSide, setActiveImageSide] = useState(null); // 'left' or 'right'
  
  // Magnifier settings
  const magnificationLevel = 2;
  const magnifierSize = 150;
  
  const leftWrapperRef = useRef(null);
  const rightWrapperRef = useRef(null);

  const handleMouseDown = (e, side) => {
    e.preventDefault();
    const wrapperRef = side === 'left' ? leftWrapperRef : rightWrapperRef;
    if (!wrapperRef.current) return;
    
    const wrapperRect = wrapperRef.current.getBoundingClientRect();
    
    const x = e.clientX - wrapperRect.left;
    const y = e.clientY - wrapperRect.top;
    
    setCursorPosition({ x, y });
    setMagnifierPosition({ 
      x: e.clientX, 
      y: e.clientY 
    });
    setShowMagnifier(true);
    setActiveImageSide(side);
  };

  const handleMouseMove = (e, side) => {
    if (showMagnifier && activeImageSide === side) {
      const wrapperRef = side === 'left' ? leftWrapperRef : rightWrapperRef;
      if (!wrapperRef.current) return;
      
      const wrapperRect = wrapperRef.current.getBoundingClientRect();
      
      const x = e.clientX - wrapperRect.left;
      const y = e.clientY - wrapperRect.top;
      
      setCursorPosition({ x, y });
      setMagnifierPosition({ 
        x: e.clientX, 
        y: e.clientY 
      });
    }
  };

  const handleMouseUp = () => {
    setShowMagnifier(false);
  };

  const handleMouseLeave = () => {
    setShowMagnifier(false);
  };

  return(
    <div className="image-container">
      <div 
        className="image-wrapper"
        ref={leftWrapperRef}
        onMouseDown={(e) => handleMouseDown(e, 'left')}
        onMouseMove={(e) => handleMouseMove(e, 'left')}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseLeave}
        style={{ position: 'relative' }}
      >
        <img src={leftImage} alt="Image 1" style={{ width: '100%', height: 'auto' }} />
        {activeLeft && (
          <img src={require('./blueBox.png')} alt="blue box" className="blue-box-overlay" />
        )}
        {leftImageMetadata && (
          <PatternDisplay metadata={leftImageMetadata} onSave={onSaveLeft} />
        )}
      </div>

      <div 
        className="image-wrapper"
        ref={rightWrapperRef}
        onMouseDown={(e) => handleMouseDown(e, 'right')}
        onMouseMove={(e) => handleMouseMove(e, 'right')}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseLeave}
        style={{ position: 'relative' }}
      >
        <img src={rightImage} alt="Image 2" style={{ width: '100%', height: 'auto' }} />
        {activeRight && (
          <img src={require('./blueBox.png')} alt="blue box" className="blue-box-overlay" />
        )}
        {rightImageMetadata && (
          <PatternDisplay metadata={rightImageMetadata} onSave={onSaveRight} />
        )}
      </div>

      {showMagnifier && activeImageSide && (
        <div 
          className="magnifier" 
          style={{
            position: 'fixed',
            left: magnifierPosition.x + 20,
            top: magnifierPosition.y - 100,
            width: `${magnifierSize}px`,
            height: `${magnifierSize}px`,
            border: '2px solid #ccc',
            borderRadius: '50%',
            overflow: 'hidden',
            pointerEvents: 'none',
            zIndex: 1000
          }}
        >
          <div
            style={{
              width: `${480 * magnificationLevel}px`,
              height: `${480 * magnificationLevel}px`,
              transform: `scale(${magnificationLevel})`,
              transformOrigin: `${0}px ${0}px`,
              position: 'absolute',
              left: `${-cursorPosition.x * (magnificationLevel - 1) - (cursorPosition.x - magnifierSize/2)}px`,
              top: `${-cursorPosition.y * (magnificationLevel - 1) - (cursorPosition.y - magnifierSize/2)}px`
            }}
          >
            {/* Clone the active wrapper for magnification */}
            {activeImageSide === 'left' ? (
              <>
                <img src={leftImage} alt="Magnified view" style={{ width: '100%', height: 'auto' }} />
                {activeLeft && (
                  <img 
                    src={require('./blueBox.png')} 
                    alt="blue box" 
                    className="blue-box-overlay" 
                    style={{ position: 'absolute', top: 0, left: 0 }}
                  />
                )}
                {leftImageMetadata && (
                  <div style={{ position: 'absolute', top: 0, left: 0 }}>
                    <PatternDisplay metadata={leftImageMetadata} onSave={null} />
                  </div>
                )}
              </>
            ) : (
              <>
                <img src={rightImage} alt="Magnified view" style={{ width: '100%', height: 'auto' }} />
                {activeRight && (
                  <img 
                    src={require('./blueBox.png')} 
                    alt="blue box" 
                    className="blue-box-overlay" 
                    style={{ position: 'absolute', top: 0, left: 0 }}
                  />
                )}
                {rightImageMetadata && (
                  <div style={{ position: 'absolute', top: 0, left: 0 }}>
                    <PatternDisplay metadata={rightImageMetadata} onSave={null} />
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default L3;