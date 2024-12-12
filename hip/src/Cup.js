import React, { useState, useRef, useEffect } from 'react';
import './Cup.css';

function Cup() {
  const [imagePairs, setImagePairs] = useState([
    { id: 1, images: [null, null] }
  ]);
  const [selectedImage, setSelectedImage] = useState(null);
  const bottomRowRef = useRef(null);
  const [currentPairIndex, setCurrentPairIndex] = useState(0);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  useEffect(() => {
  if (bottomRowRef.current) {
    const container = document.querySelector('.image-pairs-container');
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }
}, [imagePairs]);

  useEffect(() => {
    const handleKeyPress = async (event) => {
      if (event.key === 'a') {
        // Find the next empty slot
        const currentPair = imagePairs[currentPairIndex];
        if (currentPair && currentPair.images[currentImageIndex] === null) {
          await handleImageCapture(currentPairIndex, currentImageIndex);
          
          // Update indices for next capture
          if (currentImageIndex === 0) {
            setCurrentImageIndex(1);
          } else {
            setCurrentImageIndex(0);
            setCurrentPairIndex(prev => prev + 1);
          }
        }
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => {
      window.removeEventListener('keydown', handleKeyPress);
    };
  }, [currentPairIndex, currentImageIndex, imagePairs]);
  
  // Function to render points based on image dimensions
  const renderPoints = (points, imageRef,w,h) => {
    if (!points || !imageRef) return null;

    const imageRect = imageRef.getBoundingClientRect();
    
    return points.map((point, index) => (
      <div 
        key={index}
        className="point"
        style={{
          left: point.x /w* imageRect.width,
          top: point.y /h* imageRect.height
        }}
      />
    ));
  };

  const ImageWithPoints = ({ image, onClick, className, onPointsUpdate }) => {
    const imageRef = useRef(null);
    const containerRef = useRef(null);
    const [points, setPoints] = useState(image.points || []);
    const [scale, setScale] = useState(1);
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [isDragging, setIsDragging] = useState(false);
    const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
    const [draggingPointIndex, setDraggingPointIndex] = useState(null);
    const [lastDistance, setLastDistance] = useState(null);
  
    // Handle touch zoom (pinch gesture)
    const handleTouchStart = (e) => {
      if (e.touches.length === 2) {
        const touch1 = e.touches[0];
        const touch2 = e.touches[1];
        const distance = Math.hypot(
          touch2.clientX - touch1.clientX,
          touch2.clientY - touch1.clientY
        );
        setLastDistance(distance);
      } else if (e.touches.length === 1) {
        setIsDragging(true);
        setDragStart({
          x: e.touches[0].clientX - position.x,
          y: e.touches[0].clientY - position.y
        });
      }
    };
  
    const handleTouchMove = (e) => {
      e.preventDefault(); // Prevent page scrolling during touch
  
      if (e.touches.length === 2) {
        // Pinch to zoom
        const touch1 = e.touches[0];
        const touch2 = e.touches[1];
        const distance = Math.hypot(
          touch2.clientX - touch1.clientX,
          touch2.clientY - touch1.clientY
        );
  
        if (lastDistance !== null) {
          const delta = (distance - lastDistance) * 0.01;
          const newScale = Math.min(Math.max(0.1, scale + delta), 4);
          
          // Calculate the center point of the two touches
          const centerX = (touch1.clientX + touch2.clientX) / 2;
          const centerY = (touch1.clientY + touch2.clientY) / 2;
          const rect = containerRef.current.getBoundingClientRect();
          const x = centerX - rect.left;
          const y = centerY - rect.top;
  
          const newPosition = {
            x: x - (x - position.x) * (newScale / scale),
            y: y - (y - position.y) * (newScale / scale)
          };
  
          setScale(newScale);
          setPosition(newPosition);
        }
        setLastDistance(distance);
      } else if (isDragging && draggingPointIndex === null) {
        // Move image
        setPosition({
          x: e.touches[0].clientX - dragStart.x,
          y: e.touches[0].clientY - dragStart.y
        });
      } else if (draggingPointIndex !== null) {
        // Move point
        const rect = imageRef.current.getBoundingClientRect();
        const x = (e.touches[0].clientX - rect.left) / rect.width;
        const y = (e.touches[0].clientY - rect.top) / rect.height;
        
        const newPoints = [...points];
        newPoints[draggingPointIndex] = {
          x: Math.max(0, Math.min(1, x)) * image.width,
          y: Math.max(0, Math.min(1, y)) * image.height
        };
        
        setPoints(newPoints);
        if (onPointsUpdate) {
          onPointsUpdate(newPoints);
        }
      }
    };
  
    const handleTouchEnd = () => {
      setIsDragging(false);
      setDraggingPointIndex(null);
      setLastDistance(null);
    };
  
    const handleWheel = (e) => {
      e.preventDefault();
      const delta = e.deltaY * -0.01;
      const newScale = Math.min(Math.max(0.1, scale + delta), 4);
      
      const rect = containerRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      const newPosition = {
        x: x - (x - position.x) * (newScale / scale),
        y: y - (y - position.y) * (newScale / scale)
      };
  
      setScale(newScale);
      setPosition(newPosition);
    };
  
    const handleMouseDown = (e) => {
      e.preventDefault();
      setIsDragging(true);
      setDragStart({
        x: e.clientX - position.x,
        y: e.clientY - position.y
      });
    };
  
    const handleMouseMove = (e) => {
      if (isDragging && draggingPointIndex === null) {
        setPosition({
          x: e.clientX - dragStart.x,
          y: e.clientY - dragStart.y
        });
      } else if (draggingPointIndex !== null) {
        const rect = imageRef.current.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width;
        const y = (e.clientY - rect.top) / rect.height;
        
        const newPoints = [...points];
        newPoints[draggingPointIndex] = {
          x: Math.max(0, Math.min(1, x)) * image.width,
          y: Math.max(0, Math.min(1, y)) * image.height
        };
        
        setPoints(newPoints);
        if (onPointsUpdate) {
          onPointsUpdate(newPoints);
        }
      }
    };
  
    const handleMouseUp = () => {
      setIsDragging(false);
      setDraggingPointIndex(null);
    };
  
    const handlePointMouseDown = (e, index) => {
      e.stopPropagation();
      setDraggingPointIndex(index);
    };
  
    useEffect(() => {
      const preventDefault = (e) => e.preventDefault();
      containerRef.current.addEventListener('wheel', preventDefault, { passive: false });
      return () => containerRef.current.removeEventListener('wheel', preventDefault);
    }, []);
  
    const handlePointTouchStart = (e, index) => {
      e.stopPropagation();
      setDraggingPointIndex(index);
    };
  
    return (
      <div 
        ref={containerRef}
        className="image-wrapper"
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        style={{ overflow: 'hidden', position: 'relative' }}
      >
        <div
          style={{
            transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
            transformOrigin: '0 0',
            transition: isDragging ? 'none' : 'transform 0.1s',
            cursor: isDragging ? 'grabbing' : 'grab',
            position: 'relative'
          }}
        >
          <img 
            ref={imageRef}
            src={image.imageUrl} 
            alt="Captured"
            className={className}
            onClick={onClick}
            style={{ 
              cursor: 'grab',
              userSelect: 'none',
              width: '100%',
              height: '100%',
              display: 'block',
              touchAction: 'none' // Prevent default touch actions
            }}
            draggable="false"
          />
          <div className="points-overlay">
            {points.map((point, index) => (
              <div 
                key={index}
                className="point"
                style={{
                  left: `${(point.x / image.width) * 100}%`,
                  top: `${(point.y / image.height) * 100}%`,
                  width: `${10 / scale}px`,
                  height: `${10 / scale}px`,
                  cursor: 'move'
                }}
                onMouseDown={(e) => handlePointMouseDown(e, index)}
                onTouchStart={(e) => handlePointTouchStart(e, index)}
              />
            ))}
          </div>
        </div>
      </div>
    );
  };
  const fetchImageData = async (pairId, imageIndex) => {
    try {
      const response = await fetch(`http://localhost:5000/cup/image/${pairId}/${imageIndex}`);
      const data = await response.json();
      return {
        imageUrl: `http://localhost:5000${data.imageUrl}`,
        points: data.points,
        width:data.width,
        height:data.height
      };
    } catch (error) {
      console.error('Error fetching image:', error);
      return null;
    }
  };

  const handleImageCapture = async (pairIndex, imageIndex) => {
    const pairId = imagePairs[pairIndex].id;
    const imageData = await fetchImageData(pairId, imageIndex);
    
    if (imageData) {
      const newImagePairs = [...imagePairs];
      newImagePairs[pairIndex].images[imageIndex] = imageData;
      
      setSelectedImage(imageData);
      
      if (newImagePairs[pairIndex].images.every(img => img !== null)) {
        if (pairIndex === imagePairs.length - 1) {
          newImagePairs.push({ id: Date.now(), images: [null, null] });
        }
      }
      
      setImagePairs(newImagePairs);
    }
  };

  const handleImageClick = (image) => {
    setSelectedImage(image);
  };

  return (
    <div className="cup-container">
      <div className="left-area">
        {selectedImage ? (
          <ImageWithPoints 
            image={selectedImage} 
            className="large-preview"
          />
        ) : (
          <img 
            src={require('./react.png')} 
            alt="Large preview" 
            className="large-preview"
          />
        )}
      </div>
      <div className="right-area">
        <div className="image-pairs-container">
          {imagePairs.map((pair, pairIndex) => (
            <div 
              key={pair.id} 
              className="image-pair-row"
              ref={pairIndex === imagePairs.length - 1 ? bottomRowRef : null}
            >
              {pair.images.map((image, imageIndex) => (
                <div key={imageIndex} className="image-container">
                  {image ? (
                    <ImageWithPoints 
                      image={image}
                      onClick={() => handleImageClick(image)}
                      className="captured-image"
                    />
                  ) : (
                    <div className="placeholder-image">
                      <img 
                        src={require('./react.png')} 
                        alt="Placeholder" 
                      />
                      <div className="capture-overlay">
                        {pairIndex === currentPairIndex && 
                         imageIndex === currentImageIndex ? 
                         "Press 'a' to capture" : ""}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Cup;