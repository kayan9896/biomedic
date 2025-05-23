import React, { useState, useEffect, useRef } from 'react';
import AdjustmentBar from './AdjustmentBar';


function L8({
  editing,
  onSave,
  onExit,
  onReset,
  brightness,
  contrast,
  onBrightnessChange,
  onContrastChange,
  useai,
  setResetTemplate
}) {
  const [showBrightnessBar, setShowBrightnessBar] = useState(false);
  const [showContrastBar, setShowContrastBar] = useState(false);
  const [warning, setWarning] = useState(false);

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
        style={{ position: 'absolute', top: '264px', left: '920px', zIndex: 7 }}
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
          top: '272px',
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
          top: '352px',
          left: '927px',
          zIndex: 7,
          cursor: 'pointer',
        }}
        onClick={handleContrastClick}
      />
      
        {/* Reset button */}
        <img 
          className="image-button" 
          src={require('./ResetIcon.png')} 
          alt="ResetIcon" 
          style={{position:'absolute', top:'457px', left:'927px', zIndex:7, cursor:'pointer'}}
          onClick={()=>setWarning(true)}
        />
        
        
        {/* Save button */}
        <img 
          src={require('./SaveIcon.png')}
          alt="SaveIcon" 
          className="image-button"
          style={{position:'absolute', top:'552px', left:'927px', zIndex:7, cursor:'pointer'}}
          onClick={onSave}
        />
        
        {/* Exit button */}
        <img 
          src={require('./ExitIcon.png')} 
          alt="ExitIcon" 
          className="image-button"
          style={{position:'absolute', top:'633px', left:'927px', zIndex:7, cursor:'pointer'}}
          onClick={onExit}
        />

        {/* Reset button */}
        {warning && <>
          <img src={require('./EditResetWarningWindow.png')} style={{position:'absolute', top:'358px', left:'612px', zIndex:7}}/>
          <img 
            className="image-button"
            src={require('./ResettoTemplateBtn.png')} style={{position:'absolute', top:'539px', left:'671px', zIndex:7}}
            onClick={()=>{setResetTemplate(true); setWarning(false)}}
          />
          <img 
            className="image-button"
            src={((editing === 'left' && useai[0]) || ((editing === 'right' && useai[1]))) ? require('./ResettoAIBtn.png') : require('./ResettoAIBtnDisable.png')} style={{position:'absolute', top:'539px', left:'899px', zIndex:7}}
            onClick={()=>{
              if(((editing === 'left' && useai[0]) || ((editing === 'right' && useai[1])))){
                onReset(); 
                setWarning(false)
              }}}
          />
          <img 
            className="image-button"
            src={require('./CancelBtn.png')} style={{position:'absolute', top:'539px', left:'1127px', zIndex:7}}
            onClick={()=>setWarning(false)}
          />
        </>}
        
      </div>
    )
}

export default L8;