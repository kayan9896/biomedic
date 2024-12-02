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

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowImages(true);
    }, 3000);

    return () => clearTimeout(timer);
  }, [phase]);

  useEffect(() => {
    if (backendStatus.has_valid_image) {
      setCollectedImages(prev => ({
        ...prev,
        [phase]: `https://legendary-goldfish-qg6rjrrw7gv3xvg4-5000.app.github.dev/raw-image/${phase}?t=${new Date().getTime()}`
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
      await fetch(`https://legendary-goldfish-qg6rjrrw7gv3xvg4-5000.app.github.dev/start-phase/${nextPhase}`);
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
    const checkStatus = async () => {
      try {
        const response = await fetch(`https://legendary-goldfish-qg6rjrrw7gv3xvg4-5000.app.github.dev/status/${phase}`);
        const data = await response.json();
        setBackendStatus(data);
      } catch (error) {
        console.error('Error fetching status:', error);
      }
    };

    if (!showFinalGrid) {
      const statusInterval = setInterval(checkStatus, 1000);
      return () => clearInterval(statusInterval);
    }
  }, [phase, showFinalGrid]);

  const getLeftImage = () => {
    switch(phase) {
      case 1: return "./1.png";
      case 2: return "./1_2.png";
      case 3: return "./2_1.png";
      case 4: return "./2_2.png";
      default: return "./1.png";
    }
  };

  const handleRedo = async () => {
    try {
      await fetch('https://legendary-goldfish-qg6rjrrw7gv3xvg4-5000.app.github.dev/reset');
      setPhase(1);
      setShowImages(false);
      setCollectedImages({});
      setShowFinalGrid(false);
      setBackendStatus({
        is_detecting: true,
        error_message: null,
        has_valid_image: false
      });
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
      const response = await fetch(`https://legendary-goldfish-qg6rjrrw7gv3xvg4-5000.app.github.dev/image/${phase}`);
      const data = await response.json();
      setImageData(prev => ({
        ...prev,
        [phase]: {
          imageUrl: `https://legendary-goldfish-qg6rjrrw7gv3xvg4-5000.app.github.dev${data.imageUrl}`,
          points: data.points
        }
      }));
    } catch (error) {
      console.error('Error fetching image data:', error);
    }
  };

  const handlePointDrag = (phase, index, e, data) => {
    const bounds = imageBounds[phase];
    if (!bounds) return;

    const newX = Math.max(0, Math.min(data.x, bounds.width));
    const newY = Math.max(0, Math.min(data.y, bounds.height));

    const newImageData = {...imageData};
    newImageData[phase].points[index] = { x: newX, y: newY };
    setImageData(newImageData);

    // Send updated points to backend
    fetch(`https://legendary-goldfish-qg6rjrrw7gv3xvg4-5000.app.github.dev/update-points/${phase}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        points: newImageData[phase].points
      }),
    });
  };

  const handleImageLoad = (phase, e) => {
    setImageBounds(prev => ({
      ...prev,
      [phase]: {
        width: e.target.width,
        height: e.target.height
      }
    }));
  };

  const renderImage = (phase, isExpanded = false) => {
    const data = imageData[phase];
    if (!data) return null;

    return (
      <div className={`image-container ${isExpanded ? 'expanded' : ''}`}
           onClick={() => !isExpanded && setExpandedImage(phase)}>
        <img
          src={data.imageUrl}
          alt={`Phase ${phase}`}
          onLoad={(e) => handleImageLoad(phase, e)}
        />
        {data.points.map((point, index) => (
          <Draggable
            key={index}
            position={{x: point.x, y: point.y}}
            onDrag={(e, data) => handlePointDrag(phase, index, e, data)}
            disabled={!isExpanded}
          >
            <div className="point" />
          </Draggable>
        ))}
      </div>
    );
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
              <img src={getLeftImage()} alt="Reference" />
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