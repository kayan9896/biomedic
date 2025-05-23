import React, { useState, useEffect, useRef } from 'react';
import html2canvas from 'html2canvas';
import CircularProgress from './CircularProgress';
import './App.css';
import Circle from './Circle';
import Arc from './Arc';
import Ellipse from './Ellipse';
import Line from './Line';


const ProcessingAttempt = ({ subAttempts, currentSubAttempt, progress, isActive, attemptIndex,processingAttempt }) => {
  const currentImages = subAttempts[currentSubAttempt] || {};
  
  // State for Frame 1
  const [frame1Circle, setFrame1Circle] = useState(null);
  const [frame1Arc, setFrame1Arc] = useState(null);
  const [frame1Ellipse, setFrame1Ellipse] = useState(null);
  const [frame1StraightLine, setFrame1StraightLine] = useState(null);
  const [frame1SineLine, setFrame1SineLine] = useState(null);

  // State for Frame 2
  const [frame2Circle, setFrame2Circle] = useState(null);
  const [frame2Arc, setFrame2Arc] = useState(null);
  const [frame2Ellipse, setFrame2Ellipse] = useState(null);
  const [frame2StraightLine, setFrame2StraightLine] = useState(null);
  const [frame2SineLine, setFrame2SineLine] = useState(null);

  // Track unsaved changes for each frame
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState({ frame1: false, frame2: false });
 
  const [processingAttempts, setProcessingAttempts] = useState(processingAttempt);
  const [brightness1, setBrightness1] = useState(100); // 100 is normal brightness
const [brightness2, setBrightness2] = useState(100);
const [contrast1, setContrast1] = useState(100);
const [contrast2, setContrast2] = useState(100);
const [activeControl1, setActiveControl1] = useState(null);
const [activeControl2, setActiveControl2] = useState(null);

const frame1Ref = useRef(null);
  const frame2Ref = useRef(null);
  
  const captureAndSaveFrame = async (frameNumber) => {
    const frameRef = frameNumber === 1 ? frame1Ref : frame2Ref;
    
    if (!frameRef.current) return;
    
    try {
      // Use html2canvas to capture the frame with all overlays
      const canvas = await html2canvas(frameRef.current, {
        useCORS: true,
        allowTaint: true,
        backgroundColor: null,
      });
      
      // Convert canvas to blob
      canvas.toBlob(async (blob) => {
        // Create form data and append the image
        const formData = new FormData();
        formData.append('image', blob, `frame${frameNumber}_with_overlays.png`);
        
        // Send to backend
        const response = await fetch(`http://localhost:5000/save_overlay_image/${attemptIndex}/${currentSubAttempt + 1}/${frameNumber}`, {
          method: 'POST',
          body: formData,
        });
        
        if (response.ok) {
          alert(`Frame ${frameNumber} with overlays saved successfully!`);
        } else {
          throw new Error('Failed to save image with overlays');
        }
      }, 'image/png');
    } catch (err) {
      console.error('Error capturing and saving frame:', err);
      alert('Error saving image with overlays: ' + err.message);
    }
  };

// Add these style utilities
const getImageStyle = (brightness, contrast) => ({
  filter: `brightness(${(brightness + 100) / 100}) contrast(${contrast}%)`
});

// Add this component for the control bar
const ControlBar = ({ type, value, onChange, isActive, onIconClick }) => {
  return (
    <div className="control-bar">
      <div 
        className={`control-icon ${isActive ? 'active' : ''}`} 
        onClick={onIconClick}
      >
        {type === 'brightness' ? '☀️' : '◐'}
      </div>
      {isActive && (
        <div className="slider-container">
          <input
            type="range"
            min={type === 'brightness' ? -100 : 0}
            max={type === 'brightness' ? 100 : 200}
            value={value}
            onChange={(e) => onChange(parseInt(e.target.value))}
          />
          <label>{type.charAt(0).toUpperCase() + type.slice(1)}: {value}</label>
        </div>
      )}
    </div>
  );
};

// Update brightness handler for immediate feedback
const handleBrightnessChange = (frameNumber, value) => {
  if (frameNumber === 1) {
    setBrightness1(value);
  } else {
    setBrightness2(value);
  }
  
  // Optionally debounce the API call to save the adjusted image
  debouncedSaveBrightness(frameNumber, value);
};


  useEffect(() => {
    const fetchFrameMetadata = async (frameNum) => {
      if (currentImages[`image${frameNum}`]) {
        try {
          const response = await fetch(`http://localhost:5000/metadata/${attemptIndex}/${currentSubAttempt + 1}/${frameNum}`);
          if (response.ok) {
            const data = await response.json();
            if (frameNum === 1) {
              if(frame1SineLine) return
              if (data.circle) setFrame1Circle(data.circle);
              if (data.arc) setFrame1Arc(data.arc);
              if (data.ellipse) setFrame1Ellipse(data.ellipse);
              if (data.lines?.straight) setFrame1StraightLine(data.lines.straight);
              if (data.lines?.sine) setFrame1SineLine(data.lines.sine);
            } else {
              if(frame2SineLine) return
              if (data.circle) setFrame2Circle(data.circle);
              if (data.arc) setFrame2Arc(data.arc);
              if (data.ellipse) setFrame2Ellipse(data.ellipse);
              if (data.lines?.straight) setFrame2StraightLine(data.lines.straight);
              if (data.lines?.sine) setFrame2SineLine(data.lines.sine);
            }
          }
        } catch (err) {
          console.error(`Error fetching frame ${frameNum} metadata:`, err);
        }
      }
    };

    fetchFrameMetadata(1);
    fetchFrameMetadata(2);
  }, [ currentImages, attemptIndex, currentSubAttempt]);

  // Handlers for Frame 1
  const handleFrame1CenterChange = (newCenter) => {
    setFrame1Circle(prev => ({ ...prev, center: newCenter }));
    setHasUnsavedChanges(prev => ({ ...prev, frame1: true }));
  };

  const handleFrame1EdgePointChange = (newEdgePoint) => {
    setFrame1Circle(prev => ({ ...prev, edgePoint: newEdgePoint }));
    setHasUnsavedChanges(prev => ({ ...prev, frame1: true }));
  };

  const handleFrame1ArcChange = (newArcPoints) => {
    setFrame1Arc(newArcPoints);
    setHasUnsavedChanges(prev => ({ ...prev, frame1: true }));
    console.log(frame1Arc)
  };

  const handleFrame1EllipseChange = (newEllipsePoints) => {
    setFrame1Ellipse(newEllipsePoints);
    setHasUnsavedChanges(prev => ({ ...prev, frame1: true }));
  };

  const handleFrame1StraightLineChange = (newPoints) => {
    setFrame1StraightLine(newPoints);
    setHasUnsavedChanges(prev => ({ ...prev, frame1: true }));
  };

  const handleFrame1SineLineChange = (newPoints) => {
    setFrame1SineLine(newPoints);
    setHasUnsavedChanges(prev => ({ ...prev, frame1: true }));
  };

  // Handlers for Frame 2 (similar to Frame 1)
  const handleFrame2CenterChange = (newCenter) => {
    setFrame2Circle(prev => ({ ...prev, center: newCenter }));
    setHasUnsavedChanges(prev => ({ ...prev, frame2: true }));
  };

  const handleFrame2EdgePointChange = (newEdgePoint) => {
    setFrame2Circle(prev => ({ ...prev, edgePoint: newEdgePoint }));
    setHasUnsavedChanges(prev => ({ ...prev, frame2: true }));
  };

  const handleFrame2ArcChange = (newArcPoints) => {
    setFrame2Arc(newArcPoints);
    setHasUnsavedChanges(prev => ({ ...prev, frame2: true }));
  };

  const handleFrame2EllipseChange = (newEllipsePoints) => {
    setFrame2Ellipse(newEllipsePoints);
    setHasUnsavedChanges(prev => ({ ...prev, frame2: true }));
  };

  const handleFrame2StraightLineChange = (newPoints) => {
    setFrame2StraightLine(newPoints);
    setHasUnsavedChanges(prev => ({ ...prev, frame2: true }));
  };

  const handleFrame2SineLineChange = (newPoints) => {
    setFrame2SineLine(newPoints);
    setHasUnsavedChanges(prev => ({ ...prev, frame2: true }));
  };

  const handleSaveChanges = async (frameNumber) => {
    const metadata = {
      circle: frameNumber === 1 ? frame1Circle : frame2Circle,
      arc: frameNumber === 1 ? frame1Arc : frame2Arc,
      ellipse: frameNumber === 1 ? frame1Ellipse : frame2Ellipse,
      lines: {
        straight: frameNumber === 1 ? frame1StraightLine : frame2StraightLine,
        sine: frameNumber === 1 ? frame1SineLine : frame2SineLine
      },
      squareSize: 700
    };
    console.log(1, frame1Arc)

    try {
      const response = await fetch(`http://localhost:5000/metadata/${attemptIndex}/${currentSubAttempt + 1}/${frameNumber}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(metadata),
      });

      if (response.ok) {
        setHasUnsavedChanges(prev => ({
          ...prev,
          [frameNumber === 1 ? 'frame1' : 'frame2']: false
        }));
        alert(`Frame ${frameNumber} metadata saved successfully!`);
      } else {
        throw new Error('Failed to save changes');
      }
    } catch (err) {
      console.error('Error saving metadata:', err);
      alert('Error saving changes: ' + err.message);
    }
  };
  const debounce = (func, wait) => {
    let timeout;
    return (...args) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), wait);
    };
  };
  
  const debouncedSaveBrightness = debounce(async (frameNumber, value) => {
    // Your existing API call to save brightness
    try {
      const response = await fetch(`http://localhost:5000/adjust_brightness/${attemptIndex}/${currentSubAttempt + 1}/${frameNumber}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ brightness: value }),
      });
      // Handle response...
    } catch (err) {
      console.error('Error adjusting brightness:', err);
    }
  }, 500); 


  const renderFrame = (frameNumber) => {
    const image = currentImages[`image${frameNumber}`];
    const circle = frameNumber === 1 ? frame1Circle : frame2Circle;
    const arc = frameNumber === 1 ? frame1Arc : frame2Arc;
    const ellipse = frameNumber === 1 ? frame1Ellipse : frame2Ellipse;
    const straightLine = frameNumber === 1 ? frame1StraightLine : frame2StraightLine;
    const sineLine = frameNumber === 1 ? frame1SineLine : frame2SineLine;
    const frameUnsavedChanges = hasUnsavedChanges[`frame${frameNumber}`];
    const brightness = frameNumber === 1 ? brightness1 : brightness2;
  const contrast = frameNumber === 1 ? contrast1 : contrast2;
  const activeControl = frameNumber === 1 ? activeControl1 : activeControl2;
  
  const handleControlChange = (type, value) => {
    if (type === 'brightness') {
      handleBrightnessChange(frameNumber, value);
    } else if (type === 'contrast') {
      if (frameNumber === 1) {
        setContrast1(value);
      } else {
        setContrast2(value);
      }
    }
  };

    const handleCenterChange = frameNumber === 1 ? handleFrame1CenterChange : handleFrame2CenterChange;
    const handleEdgePointChange = frameNumber === 1 ? handleFrame1EdgePointChange : handleFrame2EdgePointChange;
    const handleArcChange = frameNumber === 1 ? handleFrame1ArcChange : handleFrame2ArcChange;
    const handleEllipseChange = frameNumber === 1 ? handleFrame1EllipseChange : handleFrame2EllipseChange;
    const handleStraightLineChange = frameNumber === 1 ? handleFrame1StraightLineChange : handleFrame2StraightLineChange;
    const handleSineLineChange = frameNumber === 1 ? handleFrame1SineLineChange : handleFrame2SineLineChange;
    
    return (
      <div className="frame-container">
      <div className="controls">
        <ControlBar
          type="brightness"
          value={brightness}
          onChange={(value) => handleControlChange('brightness', value)}
          isActive={activeControl === 'brightness'}
          onIconClick={() => {
            if (frameNumber === 1) {
              setActiveControl1(activeControl === 'brightness' ? null : 'brightness');
              setActiveControl2(null);
            } else {
              setActiveControl2(activeControl === 'brightness' ? null : 'brightness');
              setActiveControl1(null);
            }
          }}
        />
        <ControlBar
          type="contrast"
          value={contrast}
          onChange={(value) => handleControlChange('contrast', value)}
          isActive={activeControl === 'contrast'}
          onIconClick={() => {
            if (frameNumber === 1) {
              setActiveControl1(activeControl === 'contrast' ? null : 'contrast');
              setActiveControl2(null);
            } else {
              setActiveControl2(activeControl === 'contrast' ? null : 'contrast');
              setActiveControl1(null);
            }
          }}
        />
      </div>
      <div className="square-box" ref={frameNumber === 1 ? frame1Ref : frame2Ref}>
        {image ? (
          <>
            <img 
              src={image} 
              alt={`Frame ${frameNumber} capture`} 
              style={getImageStyle(brightness, contrast)}
            />
            
            <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: "none" }}>
              
              {circle && (
                <Circle 
                  center={circle.center}
                  edgePoint={circle.edgePoint}
                  onCenterChange={handleCenterChange}
                  onEdgePointChange={handleEdgePointChange}
                />
              )}
              {ellipse && (
                <Ellipse 
                  ellipse={ellipse} 
                  onChange={handleEllipseChange}
                />
              )}
              {arc && (
                <Arc 
                  arc={arc} 
                  onChange={handleArcChange}
                />
              )}
              {straightLine && (
                <Line 
                  squareSize={700}
                  points={straightLine}
                  onChange={handleStraightLineChange}
                />
              )}
              {sineLine && sineLine.length > 0 && (
                <Line 
                  squareSize={700}
                  points={sineLine}
                  onChange={handleSineLineChange}
                />
              )}
            </div>
            
          </>
        ) : (
          <div className="loading">Waiting for image...</div>
        )}
      </div>
      </div>
    );
  };

  const styles = `
.frame-container {
  position: relative;
}

.controls {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 10;
  display: flex;
  gap: 10px;
}

.control-bar {
  display: flex;
  align-items: center;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 20px;
  padding: 5px;
  color: white;
  transition: all 0.3s ease;
}

.control-icon {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 50%;
  transition: background 0.3s ease;
}

.control-icon:hover {
  background: rgba(255, 255, 255, 0.2);
}

.control-icon.active {
  background: rgba(255, 255, 255, 0.3);
}

.slider-container {
  display: flex;
  flex-direction: column;
  margin-left: 10px;
  overflow: hidden;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    width: 0;
    opacity: 0;
  }
  to {
    width: 150px;
    opacity: 1;
  }
}

.slider-container input {
  width: 100px;
}

.slider-container label {
  font-size: 12px;
  margin-top: 2px;
}
`;

// Add this to your component to handle clicking outside
useEffect(() => {
  const handleClickOutside = (event) => {
    if (!event.target.closest('.control-bar')) {
      setActiveControl1(null);
      setActiveControl2(null);
    }
  };

  document.addEventListener('mousedown', handleClickOutside);
  return () => {
    document.removeEventListener('mousedown', handleClickOutside);
  };
}, []);
  
    return (
      <div className={`processing-attempt ${isActive ? 'active' : ''}`}>
        <div className="top-row">
        {renderFrame(1)}
        {renderFrame(2)}
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
      <button 
        className="save-changes-button"
        onClick={() => handleSaveChanges(1)}
      >
        Save Frame 1 Changes
      </button>
      <button 
        className="save-overlay-button"
        onClick={() => captureAndSaveFrame(1)}
      >
        Save Frame 1 with Overlays
      </button>
      
      <button 
        className="save-changes-button"
        onClick={() => handleSaveChanges(2)}
      >
        Save Frame 2 Changes
      </button>
      <button 
        className="save-overlay-button"
        onClick={() => captureAndSaveFrame(2)}
      >
        Save Frame 2 with Overlays
      </button>
            
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

  const handleRetake = async () => {
    setCanProgress(false); // Disable button while processing
    try {
      const response = await fetch('http://localhost:5000/retake', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error('Failed to progress to retake');
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
              processingAttempt={processingAttempts}
            />
          )}
          <div className="control-panel">
          <button 
            onClick={handleRetake}
            className="next-frame-button"
          >
            Retake
          </button>
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
