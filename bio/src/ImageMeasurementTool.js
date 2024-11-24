import React, { useState, useRef, useEffect } from 'react';

function ImageMeasurementTool({ Url, zoom = 1 }) {
  const [points, setPoints] = useState([]);
  const [dragIndex, setDragIndex] = useState(null);
  const [distances, setDistances] = useState([]);
  const [scale, setScale] = useState(1);
  const imageRef = useRef(null);
  const containerRef = useRef(null);
  const [imageUrl, setImageUrl] = useState(null);
  const [imageSize, setImageSize] = useState({ width: 0, height: 0 });
  useEffect(() => {
    const fetchImage = async () => {
      try {
        const response = await fetch(`${Url}/api/scan-image`);
        setImageUrl(`${Url}/api/scan-image`);
      } catch (error) {
        console.error('Error fetching image:', error);
      }
    };

    fetchImage();
  }, []);

  useEffect(() => {
    fetchPoints();
  }, []);

  const fetchPoints = async () => {
    try {
      const response = await fetch(`${Url}/api/points`);
      const data = await response.json();
      setPoints(data.points);
      setDistances(data.distances);
    } catch (error) {
      console.error('Error fetching points:', error);
    }
  };

  const updatePointsOnServer = async (newPoints) => {
    try {
      const response = await fetch(`${Url}/api/points/update`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ points: newPoints }),
      });
      const data = await response.json();
      setDistances(data.distances);
    } catch (error) {
      console.error('Error updating points:', error);
    }
  };

  const getImageSrc = () => {
    try {
      return require(imageUrl);
    } catch (error) {
      return imageUrl;
    }
  };

  const handleImageClick = (e) => {
    if (dragIndex !== null) return;

    const rect = imageRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / zoom;
    const y = (e.clientY - rect.top) / zoom;
    
    // Check if click is within image boundaries
    if (x < 0 || x > imageRef.current.naturalWidth || 
        y < 0 || y > imageRef.current.naturalHeight) {
      return;
    }

    const existingPointIndex = points.findIndex(
      (point) => Math.abs(point.x - x) < 5 && Math.abs(point.y - y) < 5
    );

    if (existingPointIndex !== -1) {
      const newPoints = points.filter((_, i) => i !== existingPointIndex);
      setPoints(newPoints);
      updatePointsOnServer(newPoints);
    } else {
      const newPoints = [...points, { x, y }];
      setPoints(newPoints);
      updatePointsOnServer(newPoints);
    }
  };

  const handleDrag = (e, index) => {
    if (e.clientX === 0 && e.clientY === 0) return;
    
    const rect = imageRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / zoom;
    const y = (e.clientY - rect.top) / zoom;

    // Ensure the point stays within the image boundaries
    const boundedX = Math.max(0, Math.min(x, imageRef.current.naturalWidth));
    const boundedY = Math.max(0, Math.min(y, imageRef.current.naturalHeight));

    const newPoints = points.map((point, i) => 
      i === index ? { x: boundedX, y: boundedY } : point
    );
    setPoints(newPoints);
    updatePointsOnServer(newPoints);
  };

  const handleDragStart = (e, index) => {
    setDragIndex(index);
    const img = new Image();
    img.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
    e.dataTransfer.setDragImage(img, 0, 0);
  };

  const handleDragEnd = () => {
    setDragIndex(null);
  };

  const getMidpoint = (point1, point2) => {
    return {
      x: (point1.x + point2.x) / 2,
      y: (point1.y + point2.y) / 2
    };
  };
  const gridSize = 50; // Size of each grid square in pixels

  const createGrid = () => {
    const horizontalLines = [];
    const verticalLines = [];

    for (let i = gridSize; i < imageSize.height; i += gridSize) {
      horizontalLines.push(
        <line 
          key={`h${i}`} 
          x1="0" 
          y1={i} 
          x2={imageSize.width} 
          y2={i} 
          stroke="rgba(255,255,255,0.5)" 
          strokeWidth="1"
        />
      );
    }

    for (let i = gridSize; i < imageSize.width; i += gridSize) {
      verticalLines.push(
        <line 
          key={`v${i}`} 
          x1={i} 
          y1="0" 
          x2={i} 
          y2={imageSize.height} 
          stroke="rgba(255,255,255,0.5)" 
          strokeWidth="1"
        />
      );
    }

    return [...horizontalLines, ...verticalLines];
  };
  return (
    <div 
      style={{ 
        position: 'relative', 
        display: 'inline-block', 
        transform: `scale(${zoom})`,
        transformOrigin: 'top left'
      }}
    >
      <img 
        ref={imageRef} 
        src={imageUrl} 
        alt="Measurement Image" 
        style={{ display: 'block' }}
        onLoad={() => {
          setImageSize({
            width: imageRef.current.naturalWidth,
            height: imageRef.current.naturalHeight
          });
        }}
      />
      <svg 
        style={{ 
          position: 'absolute', 
          top: 0, 
          left: 0,
          width: '100%',
          height: '100%',
          pointerEvents: 'none'
        }}
        viewBox={`0 0 ${imageSize.width} ${imageSize.height}`}
      >
        {createGrid()}
      </svg>


      {points.length > 0 && (
        <svg 
          style={{ 
            position: 'absolute', 
            top: 0, 
            left: 0,
            width: '100%',
            height: '100%',
            pointerEvents: 'none'
          }} 
          xmlns="http://www.w3.org/2000/svg"
        >
          {points.map((point, index) => {
            if (index < points.length - 1) {
              const midpoint = getMidpoint(point, points[index + 1]);
              return (
                <g key={index}>
                  <line
                    x1={point.x}
                    y1={point.y}
                    x2={points[index + 1].x}
                    y2={points[index + 1].y}
                    stroke="black"
                    strokeWidth="2"
                  />
                  <text
                    x={midpoint.x}
                    y={midpoint.y}
                    fill="white"
                    stroke="black"
                    strokeWidth="0.5"
                    fontSize="14px"
                    textAnchor="middle"
                    dy="-5"
                  >
                    {distances[index]} px
                  </text>
                </g>
              );
            }
            return null;
          })}
        </svg>
      )}

      {points.map((point, index) => (
        <div
          key={index}
          style={{
            position: 'absolute',
            left: point.x - 5,
            top: point.y - 5,
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            backgroundColor: dragIndex === index ? 'yellow' : 'red',
            border: '2px solid white',
            cursor: 'move',
            transform: `scale(${dragIndex === index ? 1.2 : 1})`,
            transition: 'transform 0.1s, background-color 0.1s',
            zIndex: dragIndex === index ? 1000 : 1
          }}
          draggable
          onDragStart={(e) => handleDragStart(e, index)}
          onDrag={(e) => handleDrag(e, index)}
          onDragEnd={handleDragEnd}
        />
      ))}
    </div>
  );
}

export default ImageMeasurementTool;