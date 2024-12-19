import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const Viewport = () => {
  const [images, setImages] = useState([]);
  const [viewportPosition, setViewportPosition] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [viewfinder, setViewfinder] = useState(null);
  const containerRef = useRef(null);

  const PLANE_SIZE = 2000;
  const VIEWPORT_SIZE = 500;
  const ACTUAL_IMAGE_SIZE = 1000;
  const DISPLAYED_IMAGE_SIZE = 100;
  const MIN_ZOOM = 0.5;
  const MAX_ZOOM = 3;
  const ZOOM_SPEED = 0.1;
  const ZOOM_INCREASE_FACTOR = 1.1; // 10% increase
  const [isProcessing, setIsProcessing] = useState(false);

  const simulateProcessing = async () => {
    setIsProcessing(true);
    await new Promise(resolve => setTimeout(resolve, 2000));
    setIsProcessing(false);
    return true;
  };

  const ProcessingWindow = () => {
    return (
      <div style={{
        position: 'fixed',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: '200px',
        height: '200px',
        backgroundColor: '#E6EEF2',
        borderRadius: '15px',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 1000
      }}>
        <svg width="120" height="120" viewBox="0 0 120 120">
          {/* Outer circle */}
          <circle
            cx="60"
            cy="60"
            r="54"
            fill="none"
            stroke="#2C3E50"
            strokeWidth="2"
          />
  
          {/* Inner circle */}
          <circle
            cx="60"
            cy="60"
            r="45"
            fill="none"
            stroke="#1B4D3E"
            strokeWidth="2"
          />
  
          {/* Growing arc */}
          <circle
            cx="60"
            cy="60"
            r="49.5"
            fill="none"
            stroke="#3498DB"
            strokeWidth="9"
            strokeDasharray="0 312" // Start with 0 length
            strokeLinecap="round"
            style={{
              animation: 'grow 2s linear forwards',
              transformOrigin: 'center',
              transform: 'rotate(-90deg)' // Start from top
            }}
          />
        </svg>
      </div>
    );
  };
  
  // Add this CSS to your stylesheet
  const styles = `
    @keyframes grow {
      from {
        stroke-dasharray: 0 312;
      }
      to {
        stroke-dasharray: 312 312;
      }
    }
  `;

  const centerViewportOnImage = (imageX, imageY, newZoom) => {
    const imageCenter = {
      x: imageX + DISPLAYED_IMAGE_SIZE / 2,
      y: imageY + DISPLAYED_IMAGE_SIZE / 2
    };

    const newPosition = {
      x: imageCenter.x - (VIEWPORT_SIZE / newZoom) / 2,
      y: imageCenter.y - (VIEWPORT_SIZE / newZoom) / 2
    };

    return {
      x: Math.max(0, Math.min(newPosition.x, PLANE_SIZE - VIEWPORT_SIZE / newZoom)),
      y: Math.max(0, Math.min(newPosition.y, PLANE_SIZE - VIEWPORT_SIZE / newZoom))
    };
  };

// Add the styles to the document
const styleSheet = document.createElement("style");
styleSheet.innerText = styles;
document.head.appendChild(styleSheet);

  useEffect(() => {
    const handleKeyPress = async (event) => {
      if (event.key === 'x') {
        try {
          // Start processing animation
          await simulateProcessing();

          const response = await axios.get('https://legendary-goldfish-qg6rjrrw7gv3xvg4-5000.app.github.dev/image', { responseType: 'blob' });
          const imageUrl = URL.createObjectURL(response.data);
          
          setImages(prevImages => {
            let newImage;
            if (prevImages.length === 0) {
              newImage = {
                url: imageUrl,
                x: PLANE_SIZE / 2 - DISPLAYED_IMAGE_SIZE / 2,
                y: PLANE_SIZE / 2 - DISPLAYED_IMAGE_SIZE / 2
              };
            } else {
              const lastImage = prevImages[prevImages.length - 1];
              newImage = {
                url: imageUrl,
                x: lastImage.x - DISPLAYED_IMAGE_SIZE/2,
                y: lastImage.y - DISPLAYED_IMAGE_SIZE/2
              };
            }

            // Set the viewfinder
            setViewfinder({
              x: newImage.x,
              y: newImage.y,
              width: DISPLAYED_IMAGE_SIZE,
              height: DISPLAYED_IMAGE_SIZE
            });

            // Increase zoom and center viewport
            const newZoom = Math.min(MAX_ZOOM, zoom * ZOOM_INCREASE_FACTOR);
            setZoom(newZoom);

            // Center viewport on new image
            const newPosition = centerViewportOnImage(newImage.x, newImage.y, newZoom);
            setViewportPosition(newPosition);

            return [...prevImages, newImage];
          });
        } catch (error) {
          console.error('Error fetching image:', error);
        }
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [zoom]); // Added zoom to dependencies

  const handleMouseDown = (event) => {
    const startX = event.clientX;
    const startY = event.clientY;
    const startViewportX = viewportPosition.x;
    const startViewportY = viewportPosition.y;

    const handleMouseMove = (moveEvent) => {
      const deltaX = moveEvent.clientX - startX;
      const deltaY = moveEvent.clientY - startY;

      setViewportPosition({
        x: Math.max(0, Math.min(startViewportX - deltaX / zoom, PLANE_SIZE - VIEWPORT_SIZE / zoom)),
        y: Math.max(0, Math.min(startViewportY - deltaY / zoom, PLANE_SIZE - VIEWPORT_SIZE / zoom))
      });
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  const handleWheel = (event) => {
    event.preventDefault();
    const rect = containerRef.current.getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;

    const zoomPoint = {
      x: viewportPosition.x + mouseX / zoom,
      y: viewportPosition.y + mouseY / zoom
    };

    const newZoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, zoom * (1 - event.deltaY * ZOOM_SPEED)));

    const newViewportPosition = {
      x: zoomPoint.x - mouseX / newZoom,
      y: zoomPoint.y - mouseY / newZoom
    };

    setZoom(newZoom);
    setViewportPosition({
      x: Math.max(0, Math.min(newViewportPosition.x, PLANE_SIZE - VIEWPORT_SIZE / newZoom)),
      y: Math.max(0, Math.min(newViewportPosition.y, PLANE_SIZE - VIEWPORT_SIZE / newZoom))
    });
  };

  const renderViewfinder = () => {
    if (!viewfinder) return null;

    const { x, y, width, height } = viewfinder;
    const longBase = width * 1.5;
    const shortBase = width;

    return (
      <svg
        style={{
          position: 'absolute',
          left: `${x- (longBase - shortBase) / 2}px`,
          top: `${y}px`,
          width: `${longBase}px`,
          height: `${height}px`,
          pointerEvents: 'none'
        }}
      >
        <polygon
          points={`
            0,${height}
            ${longBase},${height}
            ${longBase - (longBase - shortBase) / 2},0
            ${(longBase - shortBase) / 2},0
          `}
          fill="none"
          stroke="yellow"
          strokeWidth="2"
        />
      </svg>
    );
  };

  return (
    <div
      ref={containerRef}
      style={{
        width: `${VIEWPORT_SIZE}px`,
        height: `${VIEWPORT_SIZE}px`,
        overflow: 'hidden',
        position: 'relative',
        border: '1px solid black',
        cursor: 'move'
      }}
      onMouseDown={handleMouseDown}
      onWheel={handleWheel}
    >
      <div
        style={{
          width: `${PLANE_SIZE}px`,
          height: `${PLANE_SIZE}px`,
          position: 'absolute',
          top: `${-viewportPosition.y * zoom}px`,
          left: `${-viewportPosition.x * zoom}px`,
          transform: `scale(${zoom})`,
          transformOrigin: 'top left',
          backgroundColor: '#f0f0f0'
        }}
      >
        {images.map((image, index) => (
          <img
            key={index}
            src={image.url}
            alt={`Image ${index}`}
            style={{
              position: 'absolute',
              left: `${image.x}px`,
              top: `${image.y}px`,
              width: `${DISPLAYED_IMAGE_SIZE}px`,
              height: `${DISPLAYED_IMAGE_SIZE}px`,
              objectFit: 'cover'
            }}
          />
        ))}
        {renderViewfinder()}
        {isProcessing && <ProcessingWindow />}
      </div>
    </div>
  );
};

export default Viewport;