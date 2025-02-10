import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [angle, setAngle] = useState(0);
  const [imgCount, setImgCount] = useState(0);
  const [leftImage, setLeftImage] = useState(require('./AP.png'));
  const [rightImage, setRightImage] = useState(require('./OB.png'));
  const [error, setError] = useState(null);
  const isInGreenSector = angle >= -15 && angle <= 15;
  const isInYellowSector = angle >= -45 && angle <= 45;
  const activeLeft = isInGreenSector;
  const activeRight = isInYellowSector && !isInGreenSector;
  const [isConnected, setIsConnected] = useState(false);
  const previousImgCountRef = useRef(0);  // Use useRef instead of state

  useEffect(() => {
    const fetchStates = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/states');
        const data = await response.json();
        setAngle(data.angle);
        
        // Only update images if img_count has changed
        if (data.img_count !== previousImgCountRef.current) {
          console.log('Previous count:', previousImgCountRef.current, 'New count:', data.img_count);
          previousImgCountRef.current = data.img_count;  // Update the ref
          await updateImages(data.angle);
        }

        // Clear error if angle is in valid range
        if (isInYellowSector) {
          setError(null);
        } else {
          setError("Angle out of range. Please adjust the position.");
        }
      } catch (error) {
        console.error('Error fetching states:', error);
        setError("Error connecting to server");
      }
    };

    const intervalId = setInterval(fetchStates, 50);
    return () => clearInterval(intervalId);
  }, []);

  const updateImages = async (currentAngle) => {
    try {
      // Fetch the latest image from the viewmodel
      const response = await fetch('http://localhost:5000/api/latest-image');
      const imageBlob = await response.blob();
      const imageUrl = URL.createObjectURL(imageBlob);

      // Update the appropriate image based on the angle
      if (currentAngle >= -15 && currentAngle <= 15) {
        console.log(imageUrl,previousImgCountRef)
        setLeftImage(imageUrl);
      } else if (currentAngle >= -45 && currentAngle <= 45) {
        setRightImage(imageUrl);
      }
    } catch (error) {
      console.error('Error fetching image:', error);
      setError("Error updating images");
    }
  };

  const handleConnect = async () => {
    try {
      const response = await fetch('http://localhost:5000/run2', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) throw new Error('Connection failed');
      setIsConnected(true);
    } catch (err) {
      setError('Error connecting to device: ' + err.message);
    }
  };

  return (
    <div className="app">
      {!isConnected ? (
        <div className="connection-container">
          <button onClick={handleConnect}>Connect</button>
        </div>
      ) : (
        <>
          <div className="image-container">
            <div className={`image-wrapper ${activeLeft ? 'active' : ''}`}>
              <img src={leftImage} alt="Image 1" />
              <div className="circle-mask"></div>
              {isInYellowSector && (activeLeft || !isInYellowSector) && (
                <div className="indicator-circle">
                  <div className="green-sector"></div>
                  <div className="yellow-sector"></div>
                  <div className="hand" style={{ transform: `rotate(${angle}deg)` }}></div>
                </div>
              )}
            </div>
            <div className={`image-wrapper ${activeRight ? 'active' : ''}`}>
              <img src={rightImage} alt="Image 2" />
              <div className="circle-mask"></div>
              {isInYellowSector && activeRight && (
                <div className="indicator-circle">
                  <div className="green-sector"></div>
                  <div className="yellow-sector"></div>
                  <div className="hand" style={{ transform: `rotate(${angle}deg)` }}></div>
                </div>
              )}
            </div>
          </div>
          {!isInYellowSector && (
            <div className="error-message-overlay">
              <div className="error-message-box">
                Angle out of range. Please adjust the position.
              </div>
            </div>
          )}
        </>
      )}
      <div className="toolbar">
        <span>Current Angle: {angle.toFixed(1)}°</span>
      </div>
    </div>
  );
}

export default App;