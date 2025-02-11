import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [angle, setAngle] = useState(0);
  const [ang, setAng] = useState(0);
  const [leftImage, setLeftImage] = useState(require('./AP.png'));
  const [rightImage, setRightImage] = useState(require('./OB.png'));
  const [error, setError] = useState(null);
  const [showCarmBox, setShowCarmBox] = useState(true)

  const [isConnected, setIsConnected] = useState(false);
  const previousImgCountRef = useRef(0); 
  const [rotationAngle, setRotationAngle] = useState(0);
  const [rotAng, setRotAng] = useState(0);
  const isInGreenSector = rotationAngle >= -15 && rotationAngle <= 15;
  const isInYellowSector = rotationAngle >= -45 && rotationAngle <= 45;
  const activeLeft = isInGreenSector;
  const activeRight = isInYellowSector && !isInGreenSector;
  const isRotationInRange = isInYellowSector;
  const imuon = angle >= -45 && angle <= 45;

  useEffect(() => {
    const fetchStates = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/states');
        const data = await response.json();
        setAngle(data.angle);
        setRotationAngle(data.rotation_angle);
        
        if (data.img_count !== previousImgCountRef.current) {
          previousImgCountRef.current = data.img_count;
          await updateImages(data.rotation_angle); // Pass rotation angle instead of angle
          setShowCarmBox(false); // Hide carmbox when new image is displayed
          
          // Show carmbox again after 2 seconds
          // setTimeout(() => {
          //   setShowCarmBox(true);
          // }, 2000);
        }

        if (isRotationInRange) {
          setError(null);
        } else {
          setError("Rotation angle out of range. Please adjust the position.");
        }
      } catch (error) {
        console.error('Error fetching states:', error);
        setError("Error connecting to server");
      }
    };

    const intervalId = setInterval(fetchStates, 100);
    return () => clearInterval(intervalId);
  }, []);

  const updateImages = async (currentRotationAngle) => {
    try {
      const response = await fetch('http://localhost:5000/api/latest-image');
      const imageBlob = await response.blob();
      const imageUrl = URL.createObjectURL(imageBlob);

      // Update image based on rotation angle
      if (currentRotationAngle >= -15 && currentRotationAngle <= 15) {
        setLeftImage(imageUrl);
      } else if (currentRotationAngle >= -45 && currentRotationAngle <= 45) {
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
            <div className="image-wrapper">
              <img src={leftImage} alt="Image 1" />
              {activeLeft && (
                <img 
                  src={require('./blueBox.png')} 
                  alt="blue box" 
                  className="blue-box-overlay"
                />
              )}
              <div className="circle-mask"></div>
            </div>

            <div className="image-wrapper">
              <img src={rightImage} alt="Image 2" />
              {activeRight && (
                <img 
                  src={require('./blueBox.png')} 
                  alt="blue box" 
                  className="blue-box-overlay"
                />
              )}
              <div className="circle-mask"></div>
            </div>
          </div>
          {!isRotationInRange && (
            <div className="error-message-overlay">
              <div className="error-message-box">
                Rotation angle out of range. Please adjust the position.
              </div>
            </div>
          )}

          {/* Show sliding error message for tilt angle */}
          {!imuon && (
            <div className="sliding-error" style={{
              position: 'absolute',
              right: '-300px',
              top: '863px',
              animation: 'slideIn 0.5s forwards',
              backgroundColor: '#ff4444',
              padding: '10px',
              borderRadius: '5px',
              color: 'white',
              zIndex: 1000
            }}>
              IMU Disconnected
            </div>
          )}
        </>
      )}

      <div className="toolbar">
        <span>Tilt Angle: {angle.toFixed(1)}°</span>
        <input
          type="range"
          min="-60"
          max="60"
          value={ang}
          onChange={(e) => {
            const newAngle = parseFloat(e.target.value);
            setAng(newAngle);
            fetch('http://localhost:5000/angle', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ angle: newAngle })
            })
            .catch(error => console.error('Error:', error));
          }}
          style={{
            width: '200px',
            marginLeft: '20px'
          }}
        />

        <span style={{marginLeft: '20px'}}>Rotation Angle: {rotationAngle.toFixed(1)}°</span>
        <input
          type="range"
          min="-60"
          max="60"
          value={rotAng}
          onChange={(e) => {
            const newAngle = parseFloat(e.target.value);
            setRotAng(newAngle);
            fetch('http://localhost:5000/rotation_angle', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ angle: newAngle })
            })
            .catch(error => console.error('Error:', error));
          }}
          style={{
            width: '200px',
            marginLeft: '20px'
          }}
        />
      </div>
      
      {showCarmBox && (
        <div style={{position:'absolute', top:'82px', left:'337px', zIndex:'2'}}>
          <img src={require('./carmbox.png')} alt="box" />
          <div className="hand" style={{ 
            transform: `rotate(${angle}deg)`,
            position:'absolute', 
            top:'224px', 
            left:'298px', 
            zIndex:'3' 
          }}>
            <img src={require('./tiltcarm.png')} alt="indicator" />
          </div>
          <div className="hand" style={{ 
            transform: `rotate(${rotationAngle}deg)`,
            position:'absolute', 
            top:'220px', 
            left:'750px', 
            zIndex:'3' 
          }}>
            <img src={require('./rotcarm.png')} alt="indicator" />
          </div>
        </div>
      )}
      
      {/* Only show IMU icon if angle is in range */}
      {imuon && (
        <img 
          src={require('./IMUConnectionIcon.png')} 
          style={{
            position:'absolute', 
            top:'863px', 
            left:'1825px',
            width: '84px',
            height: '84px'
          }}
        />
      )}
      <img 
        src={require('./videoConnectionIcon.png')} 
        style={{position:'absolute', top:'765px', left:'1825px'}}
      />
    </div>
  );
}

export default App;
