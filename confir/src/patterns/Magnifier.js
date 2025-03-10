import React, { useRef, useEffect } from 'react';

const Magnifier = ({ 
  show, 
  imageUrl, 
  magnification = 2,
  size = 150,
  position: { x, y } 
}) => {
  const canvasRef = useRef(null);

  useEffect(() => {

    if (!show || !imageUrl) return;

    const img = new Image();
    img.src = imageUrl;
    img.onload = () => {
      drawZoomedImage(img, x, y);
    };

    // For already loaded images, drawZoomedImage right away
    if (img.complete) {
      drawZoomedImage(img, x, y);
    }
  }, [show, x, y, imageUrl]);

  const drawZoomedImage = (img, cursorX, cursorY) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Calculate the source rectangle (area around cursor to zoom)
    const zoomBoxSize = size / magnification;
    const sourceX = Math.max(0, cursorX/960*1024 - zoomBoxSize / 2);
    const sourceY = Math.max(0, cursorY/960*1024 - zoomBoxSize / 2);
    const sourceWidth = zoomBoxSize;
    const sourceHeight = zoomBoxSize;
    console.log(sourceX, sourceY, cursorX, cursorY)
    // Draw the zoomed image portion to the canvas
    ctx.drawImage(
      img,
      sourceX, sourceY, sourceWidth, sourceHeight,
      0, 0, size, size
    );

    // Draw crosshair
    const centerX = size / 2;
    const centerY = size / 2;
    
    // Crosshair lines
    ctx.beginPath();
    ctx.strokeStyle = 'rgba(255, 0, 0, 0.8)';
    ctx.lineWidth = 1;
    
    // Horizontal line
    ctx.moveTo(centerX - 10, centerY);
    ctx.lineTo(centerX + 10, centerY);
    
    // Vertical line
    ctx.moveTo(centerX, centerY - 10);
    ctx.lineTo(centerX, centerY + 10);
    
    ctx.stroke();
    
    // Draw border
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.lineWidth = 2;
    ctx.strokeRect(0, 0, size, size);
  };

  if (!show) return null;

  return (
    <div 
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: size,
        height: size,
        zIndex: 1000,
        backgroundColor: 'white',
        boxShadow: '0 0 10px rgba(0, 0, 0, 0.5)',
        border: '1px solid #ccc',
        pointerEvents: 'none' // Don't interfere with mouse events
      }}
    >
      <canvas
        ref={canvasRef}
        width={size}
        height={size}
      />
    </div>
  );
};

export default Magnifier;