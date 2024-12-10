import React, { useState, useRef, useEffect } from 'react';
import './Cup.css';

function Cup() {
  const [imagePairs, setImagePairs] = useState([
    { id: 1, images: [null, null] }
  ]);
  const bottomRowRef = useRef(null);

  // Scroll to bottom when new row is added
  useEffect(() => {
    if (bottomRowRef.current) {
      bottomRowRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [imagePairs]);

  const handleImageCapture = (pairIndex, imageIndex) => {
    // This is where you'd handle actual image capture
    // For now, we'll simulate it by just setting a "captured" state
    
    const newImagePairs = [...imagePairs];
    newImagePairs[pairIndex].images[imageIndex] = 'captured';
    
    // Check if both images in the pair are captured
    if (newImagePairs[pairIndex].images.every(img => img === 'captured')) {
      // If this was the last pair, add a new pair
      if (pairIndex === imagePairs.length - 1) {
        newImagePairs.push({ id: Date.now(), images: [null, null] });
      }
    }
    
    setImagePairs(newImagePairs);
  };

  return (
    <div className="cup-container">
      <div className="left-area">
        <img 
          src={require('./react.png')} 
          alt="Large preview" 
          className="large-preview"
        />
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
                  {image === 'captured' ? (
                    <img 
                      src={require('./react.png')} 
                      alt={`Captured ${pairIndex}-${imageIndex}`} 
                      className="captured-image"
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