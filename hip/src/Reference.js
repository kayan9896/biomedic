import React, { useState, useEffect } from 'react';
import Draggable from 'react-draggable';

export default function Reference() {
  const [phase, setPhase] = useState(1);
  const [showImages, setShowImages] = useState(false);
  const [backendStatus, setBackendStatus] = useState({
    is_detecting: true,
    error_message: null,
    has_valid_image: false
  });
  const [collectedImages, setCollectedImages] = useState({});
  const [showFinalGrid, setShowFinalGrid] = useState(false);
  const [imageData, setImageData] = useState({});
  const [expandedImage, setExpandedImage] = useState(null);
  const [imageBounds, setImageBounds] = useState({});
  const [imageDimensions, setImageDimensions] = useState({});

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowImages(true);
    }, 3000);

    return () => clearTimeout(timer);
  }, [phase]);

  useEffect(() => {
    const startDetection = async () => {
      try {
        await fetch('http://localhost:5000/start-detection');
      } catch (error) {
        console.error('Error starting detection:', error);
      }
    };
  
    startDetection();
  
    // Cleanup function to stop detection when component unmounts
    return () => {
      fetch('http://localhost:5000/stop-detection').catch(console.error);
    };
  }, []);

  useEffect(() => {
    if (backendStatus.has_valid_image) {
      setCollectedImages(prev => ({
        ...prev,
        [phase]: `http://localhost:5000/raw-image/${phase}?t=${new Date().getTime()}`
      }));

      if (phase < 4) {
        const timer = setTimeout(() => {
          startNextPhase(phase + 1);
        }, 5000);
        return () => clearTimeout(timer);
      } else {
        const timer = setTimeout(() => {
          setShowFinalGrid(true);
        }, 3000);
        return () => clearTimeout(timer);
      }
    }
  }, [backendStatus.has_valid_image, phase]);

  const startNextPhase = async (nextPhase) => {
    try {
      await fetch(`http://localhost:5000/start-phase/${nextPhase}`);
      setPhase(nextPhase);
      setShowImages(false);
      setBackendStatus({
        is_detecting: true,
        error_message: null,
        has_valid_image: false
      });
    } catch (error) {
      console.error('Error starting next phase:', error);
    }
  };

  useEffect(() => {
    let statusInterval;
  
    const checkStatus = async () => {
      try {
        const response = await fetch(`http://localhost:5000/status/${phase}`);
        const data = await response.json();
        setBackendStatus(data);
      } catch (error) {
        console.error('Error fetching status:', error);
      }
    };
  
    if (!showFinalGrid) {
      statusInterval = setInterval(checkStatus, 1000);
    }
  
    return () => {
      if (statusInterval) {
        clearInterval(statusInterval);
      }
    };
  }, [phase, showFinalGrid]);

  const getLeftImage = () => {
    switch(phase) {
      case 1: return require("./1.png");
      case 2: return require("./1_2.png");
      case 3: return require("./2_1.png");
      case 4: return require("./2_2.png");
      default: return require("./1.png");
    }
  };

  const handleRedo = async () => {
    try {
      await fetch('http://localhost:5000/reset');
      await fetch('http://localhost:5000/start-detection'); // Start detection after reset
      setPhase(1);
      setShowImages(false);
      setCollectedImages({});
      setShowFinalGrid(false);
      setBackendStatus({
        is_detecting: true,
        error_message: null,
        has_valid_image: false
      });
      setImageData({});
      setImageDimensions({});
      setImageRatios({});
    } catch (error) {
      console.error('Error resetting:', error);
    }
  };

  useEffect(() => {
    if (backendStatus.has_valid_image) {
      fetchImageWithPoints(phase);
    }
  }, [backendStatus.has_valid_image]);

  const fetchImageWithPoints = async (phase) => {
    try {
      const response = await fetch(`http://localhost:5000/image/${phase}`);
      const data = await response.json();
      setImageData(prev => ({
        ...prev,
        [phase]: {
          imageUrl: `http://localhost:5000${data.imageUrl}?t=${new Date().getTime()}`, // Add timestamp
          points: data.points
        }
      }));
      setImageDimensions(prev => ({
        ...prev,
        [phase]: { width: data.width, height: data.height }
      }));
    } catch (error) {
      console.error('Error fetching image data:', error);
    }
  };

  const handlePointDrag = (phase, index, e, dragData) => {
    const ratio = imageRatios[phase];
    if (!ratio) return;
  
    const newImageData = {...imageData};
    newImageData[phase].points[index] = { 
      x: dragData.x / ratio.widthRatio,
      y: dragData.y / ratio.heightRatio
    };
    setImageData(newImageData);
  
    // Send updated points to backend
    fetch(`http://localhost:5000/update-points/${phase}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        points: newImageData[phase].points
      }),
    });
  };
  

  const renderImage = (phase, isExpanded = false) => {
    const data = imageData[phase];
    if (!data) return null;
  
    const containerStyle = isExpanded ? { width: '80vw', height: '80vh' } : { width: '300px', height: '300px' };
  
    return (
      <div className={`image-container ${isExpanded ? 'expanded' : ''}`}
           onClick={() => !isExpanded && setExpandedImage(phase)}
           style={containerStyle}>
        <img
          src={data.imageUrl}
          alt={`Phase ${phase}`}
          style={{ width: '100%', height: '100%', objectFit: 'contain' }}
          onLoad={(e) => handleImageLoad(phase, e)}
        />
        {data.points.map((point, index) => (
          <Draggable
            key={index}
            position={calculatePointPosition(point, phase, isExpanded)}
            onDrag={(e, dragData) => handlePointDrag(phase, index, e, dragData)}
            bounds="parent"
            disabled={!isExpanded}
          >
            <div className="point" style={{ width: '10px', height: '10px', background: 'red', borderRadius: '50%' }} />
          </Draggable>
        ))}
      </div>
    );
  };

  const [imageRatios, setImageRatios] = useState({});

const handleImageLoad = (phase, e) => {
  const { naturalWidth, naturalHeight, width, height } = e.target;
  setImageRatios(prev => ({
    ...prev,
    [phase]: { 
      widthRatio: width / naturalWidth,
      heightRatio: height / naturalHeight
    }
  }));
};

const calculatePointPosition = (point, phase, isExpanded) => {
  const ratio = imageRatios[phase];
  if (!ratio) return { x: 0, y: 0 };

  const containerStyle = isExpanded ? { width: '80vw', height: '80vh' } : { width: 300, height: 300 };
  
  return {
    x: point.x * ratio.widthRatio,
    y: point.y * ratio.heightRatio
  };
};

  if (showFinalGrid) {
    if (expandedImage) {
      return (
        <div className="expanded-view">
          {renderImage(expandedImage, true)}
          <button onClick={() => setExpandedImage(null)} className="close-button">
            Close
          </button>
        </div>
      );
    }

    return (
      <div className="final-grid">
        <div className="grid-row">
          {renderImage(1)}
          {renderImage(2)}
        </div>
        <div className="grid-row">
          {renderImage(3)}
          {renderImage(4)}
        </div>
        <button onClick={handleRedo} className="redo-button">Redo All Phases</button>
      </div>
    );
  }

  return (
    <div className="reference-container">
      {!showImages ? (
        <>
          <h2>Instructions</h2>
          <p>Some random text here. This will be replaced by images after 3 seconds.</p>
          <p>Phase: {phase}</p>
        </>
      ) : (
        <>
          <div className="image-container">
            <div className="image-area">
              <img src={getLeftImage()} style={{width:'60%', height:'60%'}} alt="Reference" />
            </div>
            <div className="image-area">
              {backendStatus.error_message && (
                <div className="error-overlay">{backendStatus.error_message}</div>
              )}
              {collectedImages[phase] ? (
                <img src={collectedImages[phase]} alt="Backend" />
              ) : (
                <img src={require("./gf.gif")} alt="Placeholder" />
              )}
            </div>
          </div>
          {backendStatus.is_detecting && (
            <div className="detection-status">Detecting image... (Phase {phase})</div>
          )}
        </>
      )}
    </div>
  );
}