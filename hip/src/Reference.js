import React, { useState, useEffect } from 'react';

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
        [phase]: `https://legendary-goldfish-qg6rjrrw7gv3xvg4-5000.app.github.dev/image/${phase}?t=${new Date().getTime()}`
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

  if (showFinalGrid) {
    return (
      <div className="final-grid">
        <div className="grid-row">
          <div className="grid-item"><img src={collectedImages[1]} alt="Image 1" /></div>
          <div className="grid-item"><img src={collectedImages[2]} alt="Image 2" /></div>
        </div>
        <div className="grid-row">
          <div className="grid-item"><img src={collectedImages[3]} alt="Image 3" /></div>
          <div className="grid-item"><img src={collectedImages[4]} alt="Image 4" /></div>
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