// App.jsx
import React, { useState, useEffect } from 'react';
import './Ap.css';
import preview1 from './1.png';
import preview2 from './2.png';
import preview3 from './3.png';
import preview4 from './4.png';

function Ap() {
  const previewImages = { 1: preview1, 2: preview2, 3: preview3, 4: preview4 };

  const [images, setImages] = useState({
    group1: { left: null, right: null },
    group2: { left: null, right: null },
    group3: { left: null, right: null },
    group4: { left: null, right: null }
  });
  
  const [activeGroup, setActiveGroup] = useState(1);
  const [activeSide, setActiveSide] = useState('left');
  const [isCapturing, setIsCapturing] = useState(false);
  const [streamUrl, setStreamUrl] = useState(null);
  const [flash, setFlash] = useState(false);
  const [reviewingGroup, setReviewingGroup] = useState(null);

  // Flash effect for active group
  useEffect(() => {
    let flashInterval;
    if (isCapturing) {
      flashInterval = setInterval(() => {
        setFlash(prev => !prev);
      }, 500);
    } else {
      setFlash(false);
    }
    return () => clearInterval(flashInterval);
  }, [isCapturing]);

  const startCapture = async () => {
    setIsCapturing(true);
    await fetch('http://localhost:5000/start_capture', { method: 'POST' });
    setStreamUrl(`http://localhost:5000/video_stream?t=${new Date().getTime()}`);
  };

  const endCapture = async () => {
    const response = await fetch('http://localhost:5000/end_capture', { method: 'POST' });
    const data = await response.json();
    setIsCapturing(false);
    setStreamUrl(null);
    return data.image;
  };

  const takePhoto = async () => {
    if (isCapturing) {
      const capturedImage = await endCapture();
      if (capturedImage) {
        const groupKey = `group${activeGroup}`;
        const imageUrl = `data:image/jpeg;base64,${capturedImage}`;
        setImages(prev => ({
          ...prev,
          [groupKey]: { 
            ...prev[groupKey], 
            [activeSide]: imageUrl
          }
        }));

        if (activeSide === 'left') {
          setActiveSide('right');
        } else {
          setActiveSide('left');
          if (activeGroup < 4) {
            setActiveGroup(prev => prev + 1);
          }
        }
      }
    } else {
      await startCapture();
    }
  };

  const reviewGroup = (group, side) => {
    if (group <= 2 && images[`group${group}`][side]) {
      setReviewingGroup({ group, side });
    }
  };

  const exitReview = () => {
    setReviewingGroup(null);
  };

  const getLargeDisplayImage = (side) => {
    if (reviewingGroup) {
      return images[`group${reviewingGroup.group}`][reviewingGroup.side];
    }

    if (isCapturing && side === activeSide) {
      return streamUrl;
    }

    const currentGroup = `group${activeGroup}`;
    const takenImage = images[currentGroup][side];
    
    if (takenImage) {
      return takenImage;
    }
    
    if (side === activeSide) {
      return previewImages[activeGroup];
    }
    
    return null;
  };

  const retakePhoto = (group, side) => {
    if (group >= 3) {
      setActiveGroup(group);
      setActiveSide(side);
    }
  };

  return (
    <div className="app-container">
      <div className="main-images">
        <div className="large-image">
          <img 
            src={getLargeDisplayImage('left')} 
            alt="Left view"
            style={{ display: getLargeDisplayImage('left') ? 'block' : 'none' }}
          />
        </div>
        <div className="large-image">
          <img 
            src={getLargeDisplayImage('right')}
            alt="Right view"
            style={{ display: getLargeDisplayImage('right') ? 'block' : 'none' }}
          />
        </div>
      </div>

      {reviewingGroup ? (
        <button onClick={exitReview}>Exit Review</button>
      ) : (
        <button onClick={takePhoto} disabled={reviewingGroup !== null}>
          {isCapturing ? 'Capture' : 'Start Capture'}
        </button>
      )}

      <div className="thumbnail-groups-container">
        <div className="thumbnail-groups">
          {[1, 2, 3, 4].map(group => (
            <div key={group} className="thumbnail-group">
              <img 
                src={previewImages[group]} 
                alt={`Group ${group}`} 
                className={`group-indicator ${
                  group === activeGroup && isCapturing && flash ? 'flash' : ''
                } ${group < activeGroup ? 'completed' : ''}`}
              />
              <div className="thumbnail-pair">
                <div 
                  className={`thumbnail ${reviewingGroup && reviewingGroup.group === group && reviewingGroup.side === 'left' ? 'reviewing' : ''}`} 
                  onClick={() => group <= 2 ? reviewGroup(group, 'left') : retakePhoto(group, 'left')}
                >
                  {images[`group${group}`].left && (
                    <img 
                      src={images[`group${group}`].left} 
                      alt=""
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                  )}
                </div>
                <div 
                  className="thumbnail" 
                  onClick={() => group <= 2 ? reviewGroup(group, 'right') : retakePhoto(group, 'right')}
                >
                  {images[`group${group}`].right && (
                    <img 
                      src={images[`group${group}`].right} 
                      alt=""
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Ap;