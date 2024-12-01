import React, { useState, useEffect } from 'react';

function Reference() {
  const [phase, setPhase] = useState(1);
  const [showImages, setShowImages] = useState(false);
  const [backendStatus, setBackendStatus] = useState({
    is_detecting: true,
    error_message: null,
    has_valid_image: false
  });
  const [backendImage, setBackendImage] = useState(null);
  const [phaseOneComplete, setPhaseOneComplete] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowImages(true);
    }, 3000);

    return () => clearTimeout(timer);
  }, [phase]);

  useEffect(() => {
    if (phaseOneComplete && phase === 1) {
      const timer = setTimeout(() => {
        startPhaseTwo();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [phaseOneComplete, phase]);

  const startPhaseTwo = async () => {
    try {
      await fetch('http://localhost:5000/start-phase-two');
      setPhase(2);
      setShowImages(false);
      setBackendImage(null);
      setBackendStatus({
        is_detecting: true,
        error_message: null,
        has_valid_image: false
      });
    } catch (error) {
      console.error('Error starting phase two:', error);
    }
  };

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await fetch(`https://legendary-goldfish-qg6rjrrw7gv3xvg4-5000.app.github.dev/status/${phase}`);
        const data = await response.json();
        setBackendStatus(data);

        if (data.has_valid_image) {
          setBackendImage(`https://legendary-goldfish-qg6rjrrw7gv3xvg4-5000.app.github.dev/image/${phase}?t=${new Date().getTime()}`);
          if (phase === 1 && !phaseOneComplete) {
            setPhaseOneComplete(true);
          }
        }
      } catch (error) {
        console.error('Error fetching status:', error);
      }
    };

    const statusInterval = setInterval(checkStatus, 1000);
    return () => clearInterval(statusInterval);
  }, [phase]);

  const getLeftImage = () => {
    return phase === 1 ? "1.png" : "1_2.png";
  };

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
              {backendImage ? (
                <img src={backendImage} alt="Backend" />
              ) : (
                <img src="gf.gif" alt="Placeholder" />
              )}
            </div>
          </div>
          {backendStatus.is_detecting && (
            <div className="detection-status">Detecting image... (Phase {phase})</div>
          )}
          {phaseOneComplete && phase === 1 && (
            <div className="phase-transition">Preparing for next phase...</div>
          )}
        </>
      )}
    </div>
  );
}


export default Reference;