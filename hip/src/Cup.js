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

  const ImageWithPoints = ({ image, onClick, className }) => {
    const imageRef = useRef(null);
    const containerRef = useRef(null);
    const [pointElements, setPointElements] = useState(null);
    const [scale, setScale] = useState(1);
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [isDragging, setIsDragging] = useState(false);
    const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  
    useEffect(() => {
      if (imageRef.current && image.points) {
        const updatePoints = () => {
          setPointElements(renderPoints(image.points, imageRef.current, image.width, image.height));
        };
  
        updatePoints();
        window.addEventListener('resize', updatePoints);
  
        return () => window.removeEventListener('resize', updatePoints);
      }
    }, [image, imageRef.current]);
  
    const handleWheel = (e) => {
      e.preventDefault();
      const delta = e.deltaY * -0.01;
      const newScale = Math.min(Math.max(scale + delta, 1), 5);
      setScale(newScale);
    };
  
    const handleMouseDown = (e) => {
      setIsDragging(true);
      setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
    };
  
    const handleMouseMove = (e) => {
      if (isDragging) {
        const newX = e.clientX - dragStart.x;
        const newY = e.clientY - dragStart.y;
        setPosition({ x: newX, y: newY });
      }
    };
  
    const handleMouseUp = () => {
      setIsDragging(false);
    };
  
    return (
      <div 
        className="zoomable-container"
        ref={containerRef}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <div 
          className="image-wrapper"
          style={{
            transform: `scale(${scale}) translate(${position.x}px, ${position.y}px)`,
            transformOrigin: '0 0'
          }}
        >
          <img 
            ref={imageRef}
            src={image.imageUrl} 
            alt="Captured"
            className={`${className} zoomable-image`}
            onClick={onClick}
            style={{ cursor: onClick ? 'pointer' : 'move' }}
          />
          <div className="points-overlay">
            {pointElements}
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