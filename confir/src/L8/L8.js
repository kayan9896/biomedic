import React, { useState, useEffect, useRef } from 'react';
import AdjustmentBar from './AdjustmentBar';


function L8({
  editing,
  onSave,
  onExit,
  onReset,
  onDelete,
  brightness,
  contrast,
  onBrightnessChange,
  onContrastChange,
}) {
  const [showBrightnessBar, setShowBrightnessBar] = useState(false);
  const [showContrastBar, setShowContrastBar] = useState(false);

  const handleBrightnessClick = () => {
    setShowBrightnessBar(!showBrightnessBar);
    if (!showBrightnessBar) setShowContrastBar(false); // Close contrast bar if open
  };

  const handleContrastClick = () => {
    setShowContrastBar(!showContrastBar);
    if (!showContrastBar) setShowBrightnessBar(false); // Close brightness bar if open
  };

  return (
    <div>
      {/* Background images */}
      <img
        src={require('./EditModeBlueBorder.png')}
        alt="EditModeBlueBorder"
        style={{ position: 'absolute', top: '0px', left: '0px', zIndex: 7, pointerEvents: 'none' }}
      />
      <img
        src={require('./EditToolbarBg.png')}
        alt="EditToolbarBg"
        style={{ position: 'absolute', top: '239px', left: '920px', zIndex: 7 }}
      />

      {/* Brightness icon and adjustment bar */}
      {showBrightnessBar && (
        <AdjustmentBar
          type="brightness"
          editing={editing}
          value={brightness}
          onChange={onBrightnessChange}
        />
      )}
      <img
        className="image-button"
        src={require('./BrightnessIcon.png')}
        alt="BrightnessIcon"
        style={{
          position: 'absolute',
          top: '251px',
          left: '927px',
          zIndex: 7,
          cursor: 'pointer',
        }}
        onClick={handleBrightnessClick}
      />
      

      {/* Contrast icon and adjustment bar */}
      {showContrastBar && (
        <AdjustmentBar
          type="contrast"
          editing={editing}
          value={contrast}
          onChange={onContrastChange}
        />
      )}
      <img
        className="image-button"
        src={require('./ContrastIcon.png')}
        alt="ContrastIcon"
        style={{
          position: 'absolute',
          top: '332px',
          left: '927px',
          zIndex: 7,
          cursor: 'pointer',
        }}
        onClick={handleContrastClick}
      />
      
        <img className="image-button" src={require('./ZoomIcon.png')} alt="ZoomIcon" style={{position:'absolute', top:'412px', left:'927px', zIndex:7}} />
        {/* Reset button */}
        <img 
          className="image-button" 
          src={require('./ResetIcon.png')} 
          alt="ResetIcon" 
          style={{position:'absolute', top:'492px', left:'927px', zIndex:7, cursor:'pointer'}}
          onClick={()=>onDelete(false)}
        />
        
        {/* Delete button */}
        <img 
          className="image-button" 
          src={require('./DeleteIcon.png')} 
          alt="DeleteIcon" 
          style={{position:'absolute', top:'572px', left:'927px', zIndex:7, cursor:'pointer'}}
          onClick={()=>onDelete(true)}
        />
        
        {/* Save button */}
        <img 
          src={require('./SaveIcon.png')}
          alt="SaveIcon" 
          className="image-button"
          style={{position:'absolute', top:'685px', left:'927px', zIndex:7, cursor:'pointer'}}
          onClick={onSave}
        />
        
        {/* Exit button */}
        <img 
          src={require('./ExitIcon.png')} 
          alt="ExitIcon" 
          className="image-button"
          style={{position:'absolute', top:'766px', left:'927px', zIndex:7, cursor:'pointer'}}
          onClick={onExit}
        />
      </div>
    )
}

export default L8;