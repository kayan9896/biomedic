
import React, { useRef, useEffect, useState } from 'react';

const Magnifier = ({ 
  show, 
  position, 
  magnification = 2, 
  size = 150, 
  imageUrl,
  offset = {x: 20, y: 20} // Offset from cursor to avoid covering the point
}) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 });
  const magnifierRef = useRef(null);
  
  
useEffect(() => {
  if (show && magnifierRef.current) {
    // Find all the SVG elements that contain patterns
    const svgElements = document.querySelectorAll('.image-wrapper svg');
    
    // Clear any previous cloned elements
    const overlayContainer = magnifierRef.current.querySelector('svg g');
    if (overlayContainer) {
      while (overlayContainer.firstChild) {
        overlayContainer.removeChild(overlayContainer.firstChild);
      }
      
      // Clone each SVG element's content and add to the magnifier
      svgElements.forEach(svg => {
        // Only clone visible elements
        if (svg.style.display !== 'none') {
          const paths = svg.querySelectorAll('path');
          paths.forEach(path => {
            const clonedPath = path.cloneNode(true);
            // Ensure the path is visible in the magnifier
            clonedPath.style.pointerEvents = 'none';
            overlayContainer.appendChild(clonedPath);
          });
          
          const circles = svg.querySelectorAll('circle');
          circles.forEach(circle => {
            const clonedCircle = circle.cloneNode(true);
            clonedCircle.style.pointerEvents = 'none';
            overlayContainer.appendChild(clonedCircle);
          });
        }
      });
    }
  }
}, [show, position.x, position.y, magnification, size]);


  // Load image dimensions when the component mounts or imageUrl changes
  useEffect(() => {
    if (imageUrl) {
      const img = new Image();
      img.onload = () => {
        setImageDimensions({ width: img.width, height: img.height });
        setImageLoaded(true);
      };
      img.src = imageUrl;
    }
  }, [imageUrl]);

  if (!show) return null;
  
  // Calculate magnifier position to make sure it stays within viewport
  const windowWidth = window.innerWidth;
  const windowHeight = window.innerHeight;
  
  // Default position at top left of cursor
  let left = position.x + offset.x;
  let top = position.y + offset.y;
  
  // Adjust if magnifier would go outside viewport
  if (left + size > windowWidth) {
    left = position.x - offset.x - size; // Place it to the left of cursor
  }
  
  if (top + size > windowHeight) {
    top = position.y - offset.y - size; // Place it above cursor
  }
  
  const magnifierStyle = {
    position: 'absolute',
    width: `${size}px`,
    height: `${size}px`,
    borderRadius: '50%',
    border: '3px solid white',
    boxShadow: '0 0 5px rgba(0,0,0,0.5)',
    overflow: 'hidden',
    zIndex: 1000,
    top: `${top}px`,
    left: `${left}px`,
    pointerEvents: 'none', // Ensure it doesn't interfere with mouse events
    backgroundColor: 'white',
  };
  
  const imgStyle = {
    position: 'absolute',
    transformOrigin: 'top left',
    transform: `scale(${magnification})`,
    // Center the magnified area on the cursor position
    left: `${-position.x * magnification + size/2}px`,
    top: `${-position.y * magnification + size/2}px`,
    maxWidth: 'none', // Override any max-width constraints
    width: '960px', // Assuming the image container size is 960px
    height: 'auto',
  };
  
  // Styles for overlaying patterns
  const overlayStyle = {
    position: 'absolute',
    width: '100%',
    height: '100%',
    pointerEvents: 'none',
    zIndex: 5,
  };
  
  const crosshairStyle = {
    position: 'absolute',
    width: '100%',
    height: '100%',
    zIndex: 10,
    pointerEvents: 'none',
  };
  
  return (
    <div ref={magnifierRef} style={magnifierStyle}>
      {/* Image being magnified */}
      <img
        src={imageUrl}
        alt="Magnified view"
        style={imgStyle}
      />
      
      {/* Clone and transform the pattern SVGs that are currently visible */}
      <div style={overlayStyle}>
        <svg width={size} height={size} style={{ overflow: 'visible' }}>
          <g transform={`translate(${size/2 - position.x * magnification}, ${size/2 - position.y * magnification}) scale(${magnification})`}>
            {/* The actual SVG content will be cloned from DOM and inserted here via useEffect */}
            {/* This serves as a placeholder for the cloned SVG content */}
          </g>
        </svg>
      </div>
      
      {/* Crosshair at the center of magnifier */}
      <svg style={crosshairStyle} width={size} height={size}>
        <line 
          x1={size/2} 
          y1={size/2 - 5} 
          x2={size/2} 
          y2={size/2 + 5} 
          stroke="red" 
          strokeWidth="1"
        />
        <line 
          x1={size/2 - 5} 
          y1={size/2} 
          x2={size/2 + 5} 
          y2={size/2} 
          stroke="red" 
          strokeWidth="1"
        />
        <circle
          cx={size/2}
          cy={size/2}
          r="2"
          fill="red"
        />
      </svg>
    </div>
  );
};

export default Magnifier;

