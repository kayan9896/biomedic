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
              {progress.stitch_progress !== 0 && 
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
  const [processingAttempts, setProcessingAttempts] = useState([]);
  const [currentAttemptIndex, setCurrentAttemptIndex] = useState(0);
  const [images, setImages] = useState({
    image1: null,
    image2: null,
    stitch: null
  });
  const [attemptsMetadata, setAttemptsMetadata] = useState([]);

  useEffect(() => {
    fetchDevices();
  }, []);

  const fetchImages = async () => {
    try {
      const currentIndex = processingAttempts.length - 1; // Get the index of the current attempt
      const checkAndFetchImage = async (endpoint) => {
        const response = await fetch(`http://localhost:5000/attempt/${currentIndex}/${endpoint}`);
        if (response.ok) {
          const blob = await response.blob();
          return URL.createObjectURL(blob);
        }
        return null;
      };
  
      const [image1Url, image2Url, stitchUrl] = await Promise.all([
        checkAndFetchImage('image1'),
        checkAndFetchImage('image2'),
        checkAndFetchImage('stitch')
      ]);
  
      setProcessingAttempts(prev => {
        const newAttempts = [...prev];
        const currentAttempt = newAttempts[newAttempts.length - 1];
        if (currentAttempt) {
          newAttempts[newAttempts.length - 1] = {
            ...currentAttempt,
            images: { image1: image1Url, image2: image2Url, stitch: stitchUrl }
          };
        }
        return newAttempts;
      });
    } catch (err) {
      console.error('Error fetching images:', err);
    }
  };

  // Polling effect for current attempt
  useEffect(() => {
    let intervalId;
    if (isConnected && processingAttempts.length > 0 && 
        currentAttemptIndex === processingAttempts.length - 1) {
      intervalId = setInterval(() => {
        fetchProgress();
        fetchImages();
      }, 1000);
    }
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [isConnected, currentAttemptIndex, processingAttempts.length]);

  // Function to fetch historical attempt images
  const fetchHistoricalAttemptImages = async (attemptIndex) => {
    if (attemptIndex === processingAttempts.length - 1) {
      // Don't fetch historical images for the current attempt
      return;
    }

    try {
      const [image1Resp, image2Resp, stitchResp] = await Promise.all([
        fetch(`http://localhost:5000/attempt/${attemptIndex}/image1`),
        fetch(`http://localhost:5000/attempt/${attemptIndex}/image2`),
        fetch(`http://localhost:5000/attempt/${attemptIndex}/stitch`)
      ]);

      const [image1Url, image2Url, stitchUrl] = await Promise.all([
        image1Resp.ok ? URL.createObjectURL(await image1Resp.blob()) : null,
        image2Resp.ok ? URL.createObjectURL(await image2Resp.blob()) : null,
        stitchResp.ok ? URL.createObjectURL(await stitchResp.blob()) : null
      ]);

      setProcessingAttempts(prev => {
        const newAttempts = [...prev];
        newAttempts[attemptIndex] = {
          ...newAttempts[attemptIndex],
          images: { image1: image1Url, image2: image2Url, stitch: stitchUrl }
        };
        return newAttempts;
      });
    } catch (err) {
      console.error('Error fetching historical attempt images:', err);
    }
  };

  const handleAttemptClick = async (index) => {
    setCurrentAttemptIndex(index);
    if (index !== processingAttempts.length - 1 && 
        !processingAttempts[index]?.images?.image1) {
      await fetchHistoricalAttemptImages(index);
    }
  };

  const startNewProcessing = async () => {
    try {
      const response = await fetch('http://localhost:5000/new_processing', {
        method: 'POST',
      });
      
      if (!response.ok) throw new Error('Failed to start new processing');
      
      const newIndex = processingAttempts.length;
      setProcessingAttempts(prev => [...prev, {
        images: { image1: null, image2: null, stitch: null },
        progress: {},
        timestamp: new Date().toISOString()
      }]);
      setCurrentAttemptIndex(newIndex);
    } catch (err) {
      setError(err.message);
      alert('Error starting new processing: ' + err.message);
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
      startNewProcessing()
    } catch (err) {
      setError(err.message);
      alert('Error connecting to device: ' + err.message);
    }
  };

  const handleRedo = async () => {
    try {
      const response = await fetch('http://localhost:5000/new_processing', {
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
            {processingAttempts.length > 0 && (
              <ProcessingAttempt 
                {...processingAttempts[currentAttemptIndex]}
                metadata={attemptsMetadata[currentAttemptIndex]}
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

          {/* Navigation Bar with Enhanced Information */}
          {processingAttempts.length > 1 && (
            <div className="navigation-bar">
              {processingAttempts.map((attempt, index) => {
                const metadata = attemptsMetadata[index];
                return (
                  <div
                    key={index}
                    className={`nav-item ${index === currentAttemptIndex ? 'active' : ''}`}
                    onClick={() => handleAttemptClick(index)}
                  >
                    <div className="attempt-header">
                      Processing {index + 1}
                      <span className="timestamp">
                        {new Date(attempt.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    {metadata && (
                      <div className="attempt-status">
                        {metadata.has_stitched_result ? 'Complete' : 'In Progress'}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;