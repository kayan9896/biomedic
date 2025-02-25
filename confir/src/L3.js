import React, { useState, useEffect, useRef } from 'react';
import PatternDisplay from './PatternDisplay';

function L3({leftImage, activeLeft, leftImageMetadata, rightImage, activeRight, rightImageMetadata, onSaveLeft, onSaveRight}) {
  return(
    <div className="image-container">
      <div className="image-wrapper">
        <img src={leftImage} alt="Image 1" />
        {activeLeft && (
          <img src={require('./blueBox.png')} alt="blue box" className="blue-box-overlay" />
        )}
        {leftImageMetadata && (
          <PatternDisplay metadata={leftImageMetadata} onSave={onSaveLeft} />
        )}
      </div>

      <div className="image-wrapper">
        <img src={rightImage} alt="Image 2" />
        {activeRight && (
          <img src={require('./blueBox.png')} alt="blue box" className="blue-box-overlay" />
        )}
        {rightImageMetadata && (
          <PatternDisplay metadata={rightImageMetadata} onSave={onSaveRight} />
        )}
      </div>
    </div>
  )
}

export default L3;