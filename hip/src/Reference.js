import React, { useState, useEffect } from 'react';
import Draggable from 'react-draggable';
import PhaseSquare from './PhaseSquare'; 

export default function Reference({setdo}) {
  const [phase, setPhase] = useState(1);
  const [backendStatus, setBackendStatus] = useState({
    is_detecting: true,
    error_message: null,
    has_valid_image: false
  });
  const [imageData, setImageData] = useState({});
  const [currentPoints, setCurrentPoints] = useState({});
  const [imageDimensions, setImageDimensions] = useState({});
  const [imageRatios, setImageRatios] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const startDetection = async () => {
      try {
        await fetch('http://localhost:5000/start-detection');
      } catch (error) {
        console.error('Error starting detection:', error);
      }
    };
  
    startDetection();
  
    return () => {
      fetch('http://localhost:5000/stop-detection').catch(console.error);
    };
  }, []);

  useEffect(() => {
    let statusInterval = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:5000/status/${phase}`);
        const data = await response.json();
        
        // Only fetch image data if we don't have it and backend says it's valid
        if (data.has_valid_image && !imageData[phase]) {
          fetchImageWithPoints(phase);
        }
        
        setBackendStatus(data);
      } catch (error) {
        console.error('Error fetching status:', error);
      }
    }, 1000);
  
    return () => clearInterval(statusInterval);
  }, [phase, imageData]);

  const fetchImageWithPoints = async (phase) => {
    try {
      const response = await fetch(`http://localhost:5000/image/${phase}`);
      const data = await response.json();
      setImageData(prev => ({
        ...prev,
        [phase]: {
          imageUrl: `http://localhost:5000${data.imageUrl}?t=${new Date().getTime()}`,
          points: data.points
        }
      }));
      setImageDimensions(prev => ({
        ...prev,
        [phase]: { width: data.width, height: data.height }
      }));
      setCurrentPoints(prev => ({
        ...prev,
        [phase]: [...data.points]
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
    setCurrentPoints(prev => {
      const newPoints = [...prev[phase]];
      newPoints[index] = { 
        x: dragData.x / ratio.widthRatio,
        y: dragData.y / ratio.heightRatio
      };
      return { ...prev, [phase]: newPoints };
    });

  };

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

  const calculatePointPosition = (point, phase) => {
    const ratio = imageRatios[phase];
    if (!ratio) return { x: 0, y: 0 };

    return {
      x: point.x * ratio.widthRatio,
      y: point.y * ratio.heightRatio
    };
  };

  const renderImage = (currentPhase) => {
    const data = imageData[currentPhase];
    if (!data) return null;
  
    return (
      <div className="image-container" style={{ width: '100%', height: '100%' }}>
        <img
          src={data.imageUrl}
          alt={`Phase ${currentPhase}`}
          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          onLoad={(e) => handleImageLoad(currentPhase, e)}
        />
        {data.points.map((point, index) => (
          <Draggable
            key={index}
            position={calculatePointPosition(point, currentPhase)}
            onDrag={(e, dragData) => handlePointDrag(currentPhase, index, e, dragData)}
            bounds="parent"
          >
            <div className="point" style={{ width: '10px', height: '10px', background: 'red', borderRadius: '50%' }} />
          </Draggable>
        ))}
      </div>
    );
  };

  const handleRetake = async () => {
    try {
      setIsLoading(true);
      // This will reset the state for the current phase and restart detection
      await fetch(`http://localhost:5000/start-phase/${phase}`);
      
      // Reset local state for this phase
      setBackendStatus({
        is_detecting: true,
        error_message: null,
        has_valid_image: false
      });
      
      // Clear the image data for this phase
      setImageData(prev => {
        const newImageData = {...prev};
        delete newImageData[phase];
        return newImageData;
      });
    } catch (error) {
      console.error('Error retaking image:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPoints = () => {
    setCurrentPoints(prev => ({
      ...prev,
      [phase]: [...imageData[phase].points]
    }));
  };

const handleConfirm = async () => {
  if (phase < 4) {
    try {
      setIsLoading(true);
      
      // Send current points to backend
      await fetch(`http://localhost:5000/update-points/${phase}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          points: currentPoints[phase]
        }),
      });

      // Update imageData with confirmed points
      setImageData(prev => ({
        ...prev,
        [phase]: {
          ...prev[phase],
          points: [...currentPoints[phase]]
        }
      }));

      // Move to next phase
      const nextPhase = phase + 1;
      await fetch(`http://localhost:5000/start-phase/${nextPhase}`);
      setPhase(nextPhase);
      setBackendStatus({
        is_detecting: true,
        error_message: null,
        has_valid_image: false
      });
    } catch (error) {
      console.error('Error confirming phase:', error);
    } finally {
      setIsLoading(false);
    }
  } else {
    setdo(true)
    console.log('All phases completed');
  }
};
  return (
    <div className="reference-container" style={{ display: 'flex' }}>
      <div className="left-area" style={{ width: '50%', height: '100vh' }}>
        {backendStatus.is_detecting && (
          <div className="detection-status">Detecting image for Phase {phase}...</div>
        )}
        {backendStatus.error_message && (
          <div className="error-overlay">{backendStatus.error_message}</div>
        )}
        {backendStatus.has_valid_image ? 
          renderImage(phase) : 
          <img 
            src={require(`/${phase}.png`)} 
            alt="Default" 
            style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
          />
        }
      </div>
      <div className="right-area" style={{ 
        width: '50%', 
        height: '100vh', 
        display: 'grid', 
        gridTemplateColumns: '1fr 1fr', 
        gridTemplateRows: '1fr 1fr' 
      }}>
        {[1, 2, 3, 4].map(p => (
          <PhaseSquare
            key={p}
            phaseNumber={p}
            currentPhase={phase}
            backendStatus={backendStatus}
            imageData={imageData}
            imageDimensions={imageDimensions}
            currentPoints={currentPoints}
            onRetake={handleRetake}
            onResetPoints={handleResetPoints}
            onConfirm={handleConfirm}
            isLoading={isLoading}
          />
        ))}
      </div>
    </div>
  );
}