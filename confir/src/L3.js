import React, { useState, useEffect, useRef } from 'react';
import PatternDisplay from './PatternDisplay';

function L3({leftImage, activeLeft, leftImageMetadata, rightImage, activeRight, rightImageMetadata}) {
    return(
      <div className="image-container">
            <div className="image-wrapper">
              <img src={leftImage} alt="Image 1" />
              {/*L5 Viewport select */}
              {activeLeft && (
                <img 
                  src={require('./blueBox.png')} 
                  alt="blue box" 
                  className="blue-box-overlay"
                />
              )}
              {/*L4 Landmarks, rendered when ther is data */}
              {leftImageMetadata && (
            <PatternDisplay metadata={leftImageMetadata} />
          )}
            </div>

            <div className="image-wrapper">
              <img src={rightImage} alt="Image 2" />
              {activeRight && (
                <img 
                  src={require('./blueBox.png')} 
                  alt="blue box" 
                  className="blue-box-overlay"
                />
              )}
              {rightImageMetadata && (
            <PatternDisplay metadata={rightImageMetadata} />
          )}
            </div>
          </div>
    )
}

export default L3;