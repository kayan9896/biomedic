import React, { useState, useEffect } from 'react';
import CircularProgress from './CircularProgress';
import './App.css';
const ProcessingAttempt = ({ subAttempts, currentSubAttempt, progress, isActive }) => {
  const currentImages = subAttempts[currentSubAttempt] || {};

  return (
    <div className={`processing-attempt ${isActive ? 'active' : ''}`}>
      <div className="top-row">
        <div className="square-box">
          {currentImages.image1 ? (
            <img src={currentImages.image1} alt="First capture" />
          ) : (
            <div className="loading">Waiting for first image...</div>
          )}
        </div>
        <div className="square-box">
          {currentImages.image2 ? (
            <img src={currentImages.image2} alt="Second capture" />
          ) : (
            <div className="loading">Waiting for second image...</div>
          )}
        </div>
      </div>
      <div className="bottom-row">
        <div className="rectangle-box">
          {currentImages.stitch ? (
            <img src={currentImages.stitch} alt="Stitched result" />
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
  const [currentSubAttempt, setCurrentSubAttempt] = useState(0);
  const [maxSubAttempts, setMaxSubAttempts] = useState(3); // 3 stages
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
      const currentIndex = processingAttempts.length - 1;
      const stage = Math.floor(currentSubAttempt / 2) + 1;
      const frameOffset = (currentSubAttempt % 2) * 2;
  
      const checkAndFetchImage = async (stage, frame) => {
        const response = await fetch(`http://localhost:5000/attempt/${currentIndex}/stage/${stage}/frame/${frame}`);
        if (response.ok) {
          const blob = await response.blob();
          return URL.createObjectURL(blob);
        }
        return null;
      };
  
      const [image1Url, image2Url, stitchUrl] = await Promise.all([
        checkAndFetchImage(stage, frameOffset + 1),
        checkAndFetchImage(stage, frameOffset + 2),
        checkAndFetchImage(stage, 'stitch')
      ]);
  
      setProcessingAttempts(prev => {
        const newAttempts = [...prev];
        const currentAttempt = { ...newAttempts[currentIndex] };
        
        if (!currentAttempt.subAttempts) {
          currentAttempt.subAttempts = [];
        }
        
        // Always create a slot for the current sub-attempt
        if (!currentAttempt.subAttempts[currentSubAttempt]) {
          currentAttempt.subAttempts[currentSubAttempt] = {};
        }
        
        // Update images only if they are available
        currentAttempt.subAttempts[currentSubAttempt] = {
          ...currentAttempt.subAttempts[currentSubAttempt],
          image1: image1Url || currentAttempt.subAttempts[currentSubAttempt].image1,
          image2: image2Url || currentAttempt.subAttempts[currentSubAttempt].image2,
          stitch: stitchUrl || currentAttempt.subAttempts[currentSubAttempt].stitch
        };
  
        newAttempts[currentIndex] = currentAttempt;
        return newAttempts;
      });
    } catch (err) {
      console.error('Error fetching images:', err);
    }
  };

  const moveToNextSubAttempt = () => {
    console.log('Current sub-attempt:', currentSubAttempt);
    console.log('Max sub-attempts:', maxSubAttempts);
    
    if (currentSubAttempt < maxSubAttempts) {
      const nextSubAttempt = currentSubAttempt + 1;
      console.log('Moving to next sub-attempt:', nextSubAttempt);
      setCurrentSubAttempt(nextSubAttempt);
    } else {
      console.log('All sub-attempts completed, starting new processing');
      startNewProcessing();
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
  }, [isConnected, currentAttemptIndex, processingAttempts.length, currentSubAttempt]);

  
  const handleSubAttemptClick = (attemptIndex, subIndex) => {
    setCurrentAttemptIndex(attemptIndex);
    setCurrentSubAttempt(subIndex);
  };

  const startNewProcessing = async () => {
    try {
      const response = await fetch('http://localhost:5000/new_processing', {
        method: 'POST',
      });
      
      if (!response.ok) throw new Error('Failed to start new processing');
      
      const newIndex = processingAttempts.length;
      setProcessingAttempts(prev => [...prev, {
        subAttempts: [],
        progress: {},
        timestamp: new Date().toISOString()
      }]);
      setCurrentAttemptIndex(newIndex);
      setCurrentSubAttempt(0);
    } catch (err) {
      setError(err.message);
      alert('Error starting new processing: ' + err.message);
    }
  };

  const resetAllAttempts = async () => {
    try {
      const response = await fetch('http://localhost:5000/reset_all', {
        method: 'POST',
      });
      
      if (!response.ok) throw new Error('Failed to reset attempts');
      
      setProcessingAttempts([]);
      setCurrentAttemptIndex(0);
      setCurrentSubAttempt(0);
      
      // Start a new processing attempt
      const newAttempt = {
        subAttempts: [],
        progress: {},
        timestamp: new Date().toISOString()
      };
      
      setProcessingAttempts([newAttempt]);
      
      // Fetch images for the first sub-attempt (stage 1, frames 1 and 2)
      fetchImages();
    } catch (err) {
      setError(err.message);
      alert('Error resetting attempts: ' + err.message);
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
              subAttempts={processingAttempts[currentAttemptIndex].subAttempts}
              currentSubAttempt={currentSubAttempt}
              progress={processingAttempts[currentAttemptIndex].progress}
              isActive={true}
            />
          )}
          <div className="control-panel">
          <button 
            onClick={moveToNextSubAttempt}
            disabled={
              !processingAttempts[currentAttemptIndex]?.subAttempts[currentSubAttempt]?.stitch ||
              currentSubAttempt >= maxSubAttempts
            }
          >
            {currentSubAttempt >= maxSubAttempts ? "Start New Attempt" : "Next"}
          </button>
            <button onClick={resetAllAttempts}>Reset All and Start New</button>
          </div>
        </div>
        
          {/* Navigation Bar with Enhanced Information */}
          {processingAttempts.length > 1 && (
            <div className="navigation-bar">
            {processingAttempts.map((attempt, attemptIndex) => (
              <React.Fragment key={attemptIndex}>
                {attempt.subAttempts && attempt.subAttempts.map((subAttempt, subIndex) => (
                  <div
                    key={`${attemptIndex}-${subIndex}`}
                    className={`nav-item ${
                      attemptIndex === currentAttemptIndex && 
                      subIndex === currentSubAttempt ? 'active' : ''
                    }`}
                    onClick={() => handleSubAttemptClick(attemptIndex, subIndex)}
                  >
                    <div className="attempt-header">
                      Attempt {attemptIndex + 1} - Stage {Math.floor(subIndex / 2) + 1}
                      <span className="timestamp">
                        {new Date(attempt.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                ))}
              </React.Fragment>
            ))}
          </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;