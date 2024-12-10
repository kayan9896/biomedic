import React, { useState, useRef, useEffect } from 'react';
import './Cup.css';

function Cup() {
  const [imagePairs, setImagePairs] = useState([
    { id: 1, images: [null, null] }
  ]);
  const [selectedImage, setSelectedImage] = useState(null); // Add state for selected image
  const bottomRowRef = useRef(null);

  const fetchImageData = async (pairId, imageIndex) => {
    try {
      const response = await fetch(`http://localhost:5000/cup/image/${pairId}/${imageIndex}`);
      const data = await response.json();
      return {
        imageUrl: `http://localhost:5000${data.imageUrl}`,
        points: data.points
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
      
      // Set the newly captured image as selected
      setSelectedImage(imageData);
      
      // Check if both images in the pair are captured
      if (newImagePairs[pairIndex].images.every(img => img !== null)) {
        // If this was the last pair, add a new pair
        if (pairIndex === imagePairs.length - 1) {
          newImagePairs.push({ id: Date.now(), images: [null, null] });
        }
      }
      
      setImagePairs(newImagePairs);
    }
  };

  // Add handler for clicking captured images
  const handleImageClick = (image) => {
    setSelectedImage(image);
  };

  return (
    <div className="cup-container">
      <div className="left-area">
        {selectedImage ? (
          <img 
            src={selectedImage.imageUrl} 
            alt="Large preview" 
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
                    <img 
                      src={image.imageUrl} 
                      alt={`Captured ${pairIndex}-${imageIndex}`} 
                      className="captured-image"
                      onClick={() => handleImageClick(image)} // Add click handler
                      style={{ cursor: 'pointer' }} // Add pointer cursor
                    />
                  ) : (
                    <div 
                      className="placeholder-image"
                      onClick={() => handleImageCapture(pairIndex, imageIndex)}
                    >
                      <img 
                        src={require('./react.png')} 
                        alt="Placeholder" 
                      />
                      <div className="capture-overlay">Click to capture</div>
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