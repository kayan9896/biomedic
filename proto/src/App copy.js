import React, { useState, useEffect } from 'react';
import CircularProgress from './CircularProgress';
import './App.css';
const ProcessingAttempt = ({ images, progress, isActive }) => {
  return (
    <div className={`processing-attempt ${isActive ? 'active' : ''}`}>
      <div className="top-row">
        <div className="square-box">
          {images.image1 ? (
            <img src={images.image1} alt="First capture" />
          ) : (
            <div className="loading">Waiting for first image...</div>
          )}
        </div>
        <div className="square-box">
          {images.image2 ? (
            <img src={images.image2} alt="Second capture" />
          ) : (
            <div className="loading">Waiting for second image...</div>
          )}
        </div>
      </div>
      <div className="bottom-row">
        <div className="rectangle-box">
          {images.stitch ? (
            <img src={images.stitch} alt="Stitched result" />
          ) : (
            <div className="loading">
              {progress.stitch_progress !== undefined && 
               progress.stitch_progress < 100 && (
                <CircularProgress percentage={progress.stitch_progress} />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

function App() {
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const [processingAttempts, setProcessingAttempts] = useState([{
    images: { image1: null, image2: null, stitch: null },
    progress: {},
    timestamp: new Date().toISOString()
  }]);
  const [currentAttemptIndex, setCurrentAttemptIndex] = useState(0);
  const [images, setImages] = useState({
    image1: null,
    image2: null,
    stitch: null
  });

  useEffect(() => {
    fetchDevices();
  }, []);

  // Initialize a new processing attempt
  const startNewProcessing = async () => {
    try {
      
      
      // Add new empty attempt to the list
      setProcessingAttempts(prev => [...prev, {
        images: { image1: null, image2: null, stitch: null },
        progress: {},
        timestamp: new Date().toISOString()
      }]);
      setCurrentAttemptIndex(processingAttempts.length);
    } catch (err) {
      setError(err.message);
      alert('Error starting new processing: ' + err.message);
    }
  };

  // Poll for updates for the current attempt
  useEffect(() => {
    let intervalId;
    if (isConnected && currentAttemptIndex === processingAttempts.length - 1) {
      intervalId = setInterval(() => {
        fetchProgress();
        fetchImages();
      }, 1000);
    }
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [isConnected, currentAttemptIndex, processingAttempts.length]);

  const fetchImages = async () => {
    try {
      const checkAndFetchImage = async (endpoint) => {
        const response = await fetch(endpoint);
        if (response.ok) {
          const blob = await response.blob();
          return URL.createObjectURL(blob);
        }
        return null;
      };

      const [image1Url, image2Url, stitchUrl] = await Promise.all([
        checkAndFetchImage('http://localhost:5000/image1'),
        checkAndFetchImage('http://localhost:5000/image2'),
        checkAndFetchImage('http://localhost:5000/stitch')
      ]);

      setProcessingAttempts(prev => {
        const newAttempts = [...prev];
        newAttempts[currentAttemptIndex] = {
          ...newAttempts[currentAttemptIndex],
          images: { image1: image1Url, image2: image2Url, stitch: stitchUrl }
        };
        return newAttempts;
      });
    } catch (err) {
      console.error('Error fetching images:', err);
    }
  };

  const fetchProgress = async () => {
    try {
      const response = await fetch('http://localhost:5000/progress');
      if (!response.ok) throw new Error('Failed to fetch progress');
      const data = await response.json();
      
      setProcessingAttempts(prev => {
        const newAttempts = [...prev];
        newAttempts[currentAttemptIndex] = {
          ...newAttempts[currentAttemptIndex],
          progress: data
        };
        return newAttempts;
      });
    } catch (err) {
      console.error('Error fetching progress:', err);
    }
  };

  const fetchDevices = async () => {
    try {
      const response = await fetch('http://localhost:5000/devices');
      if (!response.ok) throw new Error('Failed to fetch devices');
      const data = await response.json();
      setDevices(data.devices);
    } catch (err) {
      setError(err.message);
      alert('Error fetching devices: ' + err.message);
    }
  };


  const handleConnect = async () => {
    if (!selectedDevice) {
      alert('Please select a device');
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ device_name: selectedDevice }),
      });

      if (!response.ok) throw new Error('Connection failed');
      setIsConnected(true);
    } catch (err) {
      setError(err.message);
      alert('Error connecting to device: ' + err.message);
    }
  };

  const handleRedo = async () => {
    try {
      const response = await fetch('http://localhost:5000/redo', {
        method: 'POST',
      });
      
      if (!response.ok) throw new Error('Redo failed');
      
      // Clear all images
      setImages({
        image1: null,
        image2: null,
        stitch: null
      });
      
    } catch (err) {
      setError(err.message);
      alert('Error during redo: ' + err.message);
    }
  };

  return (
    <div className="App">
      {!isConnected ? (
        <div className="connection-container">
          <select
            value={selectedDevice}
            onChange={(e) => setSelectedDevice(e.target.value)}
          >
            <option value="">Select a device</option>
            {devices.map((device, index) => (
              <option key={index} value={device}>{device}</option>
            ))}
          </select>
          <button onClick={handleConnect}>Connect</button>
        </div>
      ) : (
        <div className="main-container">
          {/* Current Processing Display */}
          <div className="processing-display">
            {console.log(processingAttempts)}
            {processingAttempts.length > 0 && (
              <ProcessingAttempt 
                {...processingAttempts[currentAttemptIndex]}
                isActive={true}
              />
            )}
            <div className="control-panel">
              <button 
                onClick={startNewProcessing}
                disabled={!processingAttempts[currentAttemptIndex]?.images?.stitch}
              >
                Next Processing
              </button>
            </div>
          </div>

          {/* Navigation Bar */}
          {processingAttempts.length > 1 && (
            <div className="navigation-bar">
              {processingAttempts.map((attempt, index) => (
                <div
                  key={index}
                  className={`nav-item ${index === currentAttemptIndex ? 'active' : ''}`}
                  onClick={() => setCurrentAttemptIndex(index)}
                >
                  Processing {index + 1}
                  <span className="timestamp">
                    {new Date(attempt.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;