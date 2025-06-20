import React, { useState, useEffect, useRef } from 'react';
import PatternDisplay from './PatternDisplay';

function L3({
  leftImage,
  activeLeft,
  leftImageMetadata,
  rightImage,
  activeRight,
  rightImageMetadata,
  onSaveLeft,
  onSaveRight,
  frameRef,
  editing,
  brightness,
  contrast,
  getInstruction,
  stage
}) {

  const leftWrapperRef = useRef(null);
  const rightWrapperRef = useRef(null);

  const getFilterStyle = (brightness, contrast) => ({
    filter: `brightness(${brightness}%) contrast(${contrast}%)`,
  });

  return(
    <div className="image-container" ref={frameRef}>
      <div
        className="image-wrapper"
        ref={leftWrapperRef}
        style={{ position: 'relative' }}
      >
        <img
          src={leftImage}
          alt="Image 1"
          style={{ 
            width: '100%', 
            height: 'auto', 
            ...(leftImage !== getInstruction(stage, 'AP') ? getFilterStyle(brightness[0], contrast[0]) : {})
          }}
        />
        {activeLeft && !editing && (
          <img src={require('./L5/APViewportBlueBorder.png')} alt="blue box" className="blue-box-overlay" />
        )}
        <div className="blue-box-overlay">
        {leftImageMetadata && Object.keys(leftImageMetadata).map((group, i) => (
          <PatternDisplay
          key={i}
          group={group}
          metadata={leftImageMetadata}
          onSave={(ref) => (onSaveLeft.current[group] = ref)} // Assign ref by group
          isLeftSquare={true}
          imageUrl={leftImage}
          editing={editing}
        />
        ))}
        </div>
      </div>

      <div
        className="image-wrapper"
        ref={rightWrapperRef}
        style={{ position: 'relative' }}
      >
        <img
          src={rightImage}
          alt="Image 2"
          style={{ 
            width: '100%', 
            height: 'auto', 
            ...((rightImage !== getInstruction(stage, 'OB')) ? getFilterStyle(brightness[1], contrast[1]) : {})
          }}
        />
        {activeRight && !editing && (
          <img src={require('./L5/OBViewportBlueBorder.png')} alt="blue box" className="blue-box-overlay" />
        )}
        <div className="blue-box-overlay">
        {rightImageMetadata && Object.keys(rightImageMetadata).map((group, i) => (
          <PatternDisplay
          key={i}
          group={group}
          metadata={rightImageMetadata}
          onSave={(ref) => (onSaveRight.current[group] = ref)} // Assign ref by group
          isLeftSquare={false}
          imageUrl={rightImage}
          editing={editing}
        />
        ))}
        </div>
      </div>
      <img src={require('./L5/PartingLine.png')} style={{position:'absolute', left: '958px', top: '0px'}}/>

    </div>
  );
}

export default L3;