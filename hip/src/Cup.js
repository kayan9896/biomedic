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
    const lastTouchDistance = useRef(null);
  
    useEffect(() => {
      if (imageRef.current) {
        const updatePoints = () => {
          setPoints(image.points || []);
        };
  
        updatePoints();
        window.addEventListener('resize', updatePoints);
        return () => window.removeEventListener('resize', updatePoints);
      }
    }, [image]);
  
    const handleWheel = (e) => {
      e.preventDefault();
      const delta = e.deltaY * -0.01;
      updateScale(delta, e.clientX, e.clientY);
    };
  
    const updateScale = (delta, clientX, clientY) => {
      const rect = containerRef.current.getBoundingClientRect();
      const x = clientX - rect.left;
      const y = clientY - rect.top;
  
      const newScale = Math.min(Math.max(0.1, scale + delta), 4);
      const newPosition = {
        x: x - (x - position.x) * (newScale / scale),
        y: y - (y - position.y) * (newScale / scale)
      };
  
      setScale(newScale);
      setPosition(newPosition);
    };
  
    const handleStart = (clientX, clientY) => {
      setIsDragging(true);
      setDragStart({
        x: clientX - position.x,
        y: clientY - position.y
      });
    };
  
    const handleMove = (clientX, clientY) => {
      if (isDragging && draggingPointIndex === null) {
        setPosition({
          x: clientX - dragStart.x,
          y: clientY - dragStart.y
        });
      } else if (draggingPointIndex !== null) {
        const rect = imageRef.current.getBoundingClientRect();
        const x = (clientX - rect.left) / rect.width;
        const y = (clientY - rect.top) / rect.height;
        
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
  
    const handleEnd = () => {
      setIsDragging(false);
      setDraggingPointIndex(null);
      lastTouchDistance.current = null;
    };
  
    const handlePointStart = (e, index) => {
      e.stopPropagation();
      setDraggingPointIndex(index);
    };
  
    // Mouse event handlers
    const handleMouseDown = (e) => {
      e.preventDefault();
      handleStart(e.clientX, e.clientY);
    };
  
    const handleMouseMove = (e) => {
      handleMove(e.clientX, e.clientY);
    };
  
    // Touch event handlers
    const handleTouchStart = (e) => {
      if (e.touches.length === 1) {
        handleStart(e.touches[0].clientX, e.touches[0].clientY);
      } else if (e.touches.length === 2) {
        lastTouchDistance.current = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
      }
    };
  
    const handleTouchMove = (e) => {
      e.preventDefault(); // Prevent scrolling when touching the element
      if (e.touches.length === 1) {
        handleMove(e.touches[0].clientX, e.touches[0].clientY);
      } else if (e.touches.length === 2) {
        const distance = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
        
        if (lastTouchDistance.current) {
          const delta = (distance - lastTouchDistance.current) * 0.01;
          const centerX = (e.touches[0].clientX + e.touches[1].clientX) / 2;
          const centerY = (e.touches[0].clientY + e.touches[1].clientY) / 2;
          updateScale(delta, centerX, centerY);
        }
        
        lastTouchDistance.current = distance;
      }
    };
  
    useEffect(() => {
      const preventDefault = (e) => e.preventDefault();
      containerRef.current.addEventListener('wheel', preventDefault, { passive: false });
      containerRef.current.addEventListener('touchmove', preventDefault, { passive: false });
      return () => {
        containerRef.current.removeEventListener('wheel', preventDefault);
        containerRef.current.removeEventListener('touchmove', preventDefault);
      };
    }, []);
  
    return (
      <div 
        ref={containerRef}
        className="image-wrapper"
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleEnd}
        onMouseLeave={handleEnd}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleEnd}
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
              display: 'block'
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
                  cursor: 'move'
                }}
                onMouseDown={(e) => handlePointStart(e, index)}
                onTouchStart={(e) => handlePointStart(e, index)}
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