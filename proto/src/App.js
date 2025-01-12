import React, { useState, useEffect } from 'react';
import CircularProgress from './CircularProgress';
import './App.css';
import Circle from './Circle';
import Arc from './Arc';
import Ellipse from './Ellipse';
import Line from './Line';


const ProcessingAttempt = ({ subAttempts, currentSubAttempt, progress, isActive, attemptIndex }) => {
  const currentImages = subAttempts[currentSubAttempt] || {};
  const [frame1Metadata, setFrame1Metadata] = useState(null);
  const [frame2Metadata, setFrame2Metadata] = useState(null);
  const [metadata, setMetadata] = useState(null);
  // State for Circle
  const [ccenter, setcCenter] = useState([100, 100]);
  const [edgePoint, setEdgePoint] = useState([150, 100]);
  // State for Arc
  const [arcPoints, setArcPoints] = useState([[50, 50], [100, 100], [100, 0]]);
  // State for Ellipse
  const [ellipsePoints, setEllipsePoints] = useState([[50, 100], [100, 50], [150, 100]]);
  // State for Lines
  const [straightLinePoints, setStraightLinePoints] = useState([[200, 200], [300, 300]]);
  const [sinePoints, setSinePoints] = useState([]);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  
  // Fetch initial metadata
  useEffect(() => {
    const fetchFrameMetadata = async () => {
      if (currentImages.image1) {
        try {
          const response = await fetch(`http://localhost:5000/metadata/${attemptIndex}/${currentSubAttempt + 1}/1`);
          if (response.ok) {
            const data = await response.json();
            setFrame1Metadata(data);
          }
        } catch (err) {
          console.error('Error fetching frame 1 metadata:', err);
        }
      }

      if (currentImages.image2) {
        try {
          const response = await fetch(`http://localhost:5000/metadata/${attemptIndex}/${currentSubAttempt + 1}/2`);
          if (response.ok) {
            const data = await response.json();
            setFrame2Metadata(data);
          }
        } catch (err) {
          console.error('Error fetching frame 2 metadata:', err);
        }
      }
    };

    fetchFrameMetadata();
  }, [currentImages, attemptIndex, currentSubAttempt]);

  // Handlers for Circle
  const handleCenterChange = (newCenter) => {
    setcCenter(newCenter);
    setHasUnsavedChanges(true);
  };

  const handleEdgePointChange = (newEdgePoint) => {
    setEdgePoint(newEdgePoint);
    setHasUnsavedChanges(true);
  };

  // Handler for Arc
  const handleArcChange = (newArcPoints) => {
    setArcPoints(newArcPoints);
    setHasUnsavedChanges(true);
  };

  // Handler for Ellipse
  const handleEllipseChange = (newEllipsePoints) => {
    setEllipsePoints(newEllipsePoints);
    setHasUnsavedChanges(true);
  };

  // Handlers for Lines
  const handleStraightLineChange = (newPoints) => {
    setStraightLinePoints(newPoints);
    setHasUnsavedChanges(true);
  };

  const handleSineLineChange = (newPoints) => {
    setSinePoints(newPoints);
    setHasUnsavedChanges(true);
  };

  const handleSaveChanges = async () => {
    if (!metadata) return;

    const updatedMetadata = {
      ...metadata,
      circle: {
        center: ccenter,
        edgePoint: edgePoint
      },
      arc: arcPoints,
      ellipse: ellipsePoints,
      lines: {
        straight: straightLinePoints,
        sine: sinePoints
      },
      squareSize: metadata.squareSize
    };

    try {
      const response = await fetch('http://localhost:5000/metadata', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedMetadata),
      });

      if (response.ok) {
        setHasUnsavedChanges(false);
        alert('Changes saved successfully!');
      } else {
        throw new Error('Failed to save changes');
      }
    } catch (err) {
      console.error('Error saving metadata:', err);
      alert('Error saving changes: ' + err.message);
    }
  };
  
    // Only render the visualization components when metadata is available
    const renderVisualizations = (metadata) => {
      if (!metadata) return null;
  
      return (
        <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: "none" }}>
        <Arc 
          arc={arcPoints} 
          onChange={handleArcChange}
        />
        <Circle 
          center={ccenter}
          edgePoint={edgePoint}
          onCenterChange={handleCenterChange}
          onEdgePointChange={handleEdgePointChange}
        />
        <Ellipse 
          ellipse={ellipsePoints}
          onChange={handleEllipseChange}
        />
        <Line 
          squareSize={metadata?.squareSize || 300}
          points={straightLinePoints}
          onChange={handleStraightLineChange}
        />
        <Line 
          squareSize={metadata?.squareSize || 300}
          points={sinePoints}
          onChange={handleSineLineChange}
        />
      </div>
      );
    };
  
    return (
      <div className={`processing-attempt ${isActive ? 'active' : ''}`}>
        <div className="top-row">
        <div className="square-box">
          {currentImages.image1 ? (
            <>
              <img src={currentImages.image1} alt="First capture" />
              {renderVisualizations(frame1Metadata)}
            </>
          ) : (
            <div className="loading">Waiting for first image...</div>
          )}
        </div>
        <div className="square-box">
          {currentImages.image2 ? (
            <>
              <img src={currentImages.image2} alt="Second capture" />
              {renderVisualizations(frame2Metadata)}
            </>
          ) : (
            <div className="loading">Waiting for second image...</div>
          )}
        </div>
      </div>
      <div className="bottom-row">
        <div className="rectangle-box">
          {(currentImages.image1&&currentImages.image2&&currentImages.stitch)? (
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
      {hasUnsavedChanges && (
        <div className="save-changes-container">
          <button 
            className="save-changes-button"
            onClick={handleSaveChanges}
          >
            Save Changes
          </button>
        </div>
      )}
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
  const [maxSubAttempts, setMaxSubAttempts] = useState(3); 
  const [canProgress, setCanProgress] = useState(true);
 
  useEffect(() => {
    fetchDevices();
  }, []);

  const fetchImages = async () => {
    try {
      const currentIndex = processingAttempts.length - 1;
      const stage = currentSubAttempt===0?1:currentSubAttempt;
      const frameOffset = currentSubAttempt===1?2:0;
  
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
    if (currentSubAttempt < maxSubAttempts) {
      // Create a placeholder for the next sub-attempt immediately
      setProcessingAttempts(prev => {
        const newAttempts = [...prev];
        const currentAttempt = { ...newAttempts[currentAttemptIndex] };
        
        if (!currentAttempt.subAttempts) {
          currentAttempt.subAttempts = [];
        }
        
        // Create a placeholder for the next sub-attempt if it doesn't exist
        if (!currentAttempt.subAttempts[currentSubAttempt + 1]) {
          currentAttempt.subAttempts[currentSubAttempt + 1] = {};
        }
        
        newAttempts[currentAttemptIndex] = currentAttempt;
        return newAttempts;
      });
  
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
      const newAttempt = {
        subAttempts: Array.from({length: maxSubAttempts + 1}, () => ({})),
        progress: {},
        timestamp: new Date().toISOString()
      };
      
      setProcessingAttempts(prev => [...prev, newAttempt]);
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

  const handleMock = async () => {
    try {
      const response = await fetch('http://localhost:5000/mock', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) throw new Error('Connection failed');
      setIsConnected(true);
      startNewProcessing()
    } catch (err) {
      setError(err.message);
      alert('Error connecting to device: ' + err.message);
    }
  };

  const handleNextFrame = async () => {
    setCanProgress(false); // Disable button while processing
    try {
      const response = await fetch('http://localhost:5000/next_frame', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error('Failed to progress to next frame');
      }
      
      // Re-enable button after a short delay to ensure frame is processed
      setTimeout(() => setCanProgress(true), 1000);
      
    } catch (err) {
      console.error('Error progressing to next frame:', err);
      alert('Error progressing to next frame: ' + err.message);
      setCanProgress(true);
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
          <button onClick={handleMock}>Mock</button>
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
              attemptIndex = {currentAttemptIndex}
            />
          )}
          <div className="control-panel">
          <button 
            onClick={handleNextFrame}
            disabled={!canProgress}
            className="next-frame-button"
          >
            Process Next Frame
          </button>
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
        
        {processingAttempts.length > 0 && (
          <div className="navigation-bar">
            {processingAttempts.map((attempt, attemptIndex) => (
              <React.Fragment key={attemptIndex}>
                {Array.from({length: maxSubAttempts + 1}, (_, subIndex) => (
                  <div
                    key={`${attemptIndex}-${subIndex}`}
                    className={`nav-item ${
                      attemptIndex === currentAttemptIndex && 
                      subIndex === currentSubAttempt ? 'active' : ''
                    } ${attempt.subAttempts && attempt.subAttempts[subIndex]?.stitch ? 'completed' : ''}`}
                    onClick={() => handleSubAttemptClick(attemptIndex, subIndex)}
                  >
                    <div className="attempt-header">
                      Attempt {attemptIndex + 1} - Stage {subIndex + 1}
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