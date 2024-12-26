import React, { useState, useEffect } from 'react';
import CircularProgress from './CircularProgress';
import './App.css';

function App() {
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState({});
  const [images, setImages] = useState({
    image1: null,
    image2: null,
    stitch: null
  });

  // Fetch devices when component mounts
  useEffect(() => {
    fetchDevices();
  }, []);

  // Poll for progress and images when connected
  useEffect(() => {
    let intervalId;
    if (isConnected) {
      intervalId = setInterval(() => {
        fetchProgress();
        fetchImages();
      }, 1000); // Poll every second
    }
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [isConnected]);

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

  const fetchProgress = async () => {
    try {
      const response = await fetch('http://localhost:5000/progress');
      if (!response.ok) throw new Error('Failed to fetch progress');
      const data = await response.json();
      setProgress(data);
    } catch (err) {
      console.error('Error fetching progress:', err);
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

  const fetchImages = async () => {
    try {
      const checkAndFetchImage = async (endpoint, currentUrl) => {
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

      setImages({
        image1: image1Url,
        image2: image2Url,
        stitch: stitchUrl
      });
    } catch (err) {
      console.error('Error fetching images:', err);
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
        <div className="display-container">
          <div className="control-panel">
            <button onClick={handleRedo} className="redo-button">
              Redo Capture
            </button>
          </div>
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
      )}
    </div>
  );
}

export default App;