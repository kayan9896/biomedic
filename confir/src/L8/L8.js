import React, { useState, useEffect, useRef } from 'react';

function L8({editing, onSave, onExit, onReset, onDelete, bright, setBright}) {
    const [showBright, setShowBright] = useState(false)
    return(
      <div>
        <img src={require('./EditModeBlueBorder.png')} alt="EditModeBlueBorder" style={{position:'absolute', top:'0px', left:'0px', zIndex:7, pointerEvents:'none'}}/>
        <img src={require('./EditToolbarBg.png')} alt="EditToolbarBg" style={{position:'absolute', top:'239px', left:'920px', zIndex:7}}/>
        {showBright&&<div style={{
            width: '180px',
            height: '60px',
            backgroundColor: '#ccc',
            border: '2px dashed #ccc',
            borderRadius: '30px',
            marginLeft: '10px',
            padding: '0 15px',
            alignItems: 'center',
            justifyContent: 'revert',
            position:'absolute', top:'251px', left: editing === 'left'?'970px':'740px', zIndex:7
        }}>
            <div style={{
              position: 'absolute',
              top: '50%',
              width: `calc(100% - 30px)`,
              height: '4px',
              backgroundColor: '#ddd',
              borderRadius: '2px',
              pointerEvents: 'none',
            }}></div>
            <div style={{
              position: 'absolute',
              height: '4px',
              backgroundColor: '#2196F3',
              borderRadius: '2px',
              pointerEvents: 'none',
              top: '50%',
              left: editing === 'left' ? bright[0]>0?'50%':`${50+bright[0]/2/90*67}%` : bright[1]>0?'50%':`${50+bright[1]/2/90*67}%`,
              width: editing === 'left' ? `${Math.abs(bright[0]/2/90*67)}%` : `${Math.abs(bright[1]/2/90*67)}%`
            }}></div>
            <input type="range" min="-100" max="100" value={editing === 'left' ? bright[0]: bright[1]} onChange={(e) => setBright((prev)=>{
              console.log(prev)
              let tmp = [...prev] 
              editing === 'left' ? tmp[0] = Number(e.target.value) : tmp[1] = Number(e.target.value)
              return tmp
              })}/>
            <div style={{position:'absolute',bottom:'1%',left:'50%'}}>{editing === 'left' ? bright[0]: bright[1]}%</div>
        </div>}
        <img className="image-button" src={require('./BrightnessIcon.png')} alt="BrightnessIcon" style={{position:'absolute', top:'251px', left:'927px', zIndex:7}} onClick={()=>setShowBright(!showBright)}/>
        <img className="image-button" src={require('./ContrastIcon.png')} alt="ContrastIcon" style={{position:'absolute', top:'332px', left:'927px', zIndex:7}}/>
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