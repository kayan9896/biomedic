import React, { useState, useEffect, useRef } from 'react';

function L8({setEditing}) {
    return(
      <div>
        <img className="image-button" src={require('./EditModeBlueBorder.png')} alt="EditModeBlueBorder" style={{position:'absolute', top:'0px', left:'0px', zIndex:7}}/>
        <img className="image-button" src={require('./EditToolbarBg.png')} alt="EditToolbarBg" style={{position:'absolute', top:'239px', left:'920px', zIndex:7}}/>
        <img className="image-button" src={require('./BrightnessIcon.png')} alt="BrightnessIcon" style={{position:'absolute', top:'251px', left:'927px', zIndex:7}}/>
        <img className="image-button" src={require('./ContrastIcon.png')} alt="ContrastIcon" style={{position:'absolute', top:'332px', left:'927px', zIndex:7}}/>
        <img className="image-button" src={require('./ZoomIcon.png')} alt="ZoomIcon" style={{position:'absolute', top:'412px', left:'927px', zIndex:7}}/>
        <img className="image-button" src={require('./ResetIcon.png')} alt="ResetIcon" style={{position:'absolute', top:'492px', left:'927px', zIndex:7}}/>
        <img className="image-button" src={require('./DeleteIcon.png')} alt="DeleteIcon" style={{position:'absolute', top:'572px', left:'927px', zIndex:7}}/>
        <img 
          src={require('./SaveIcon.png')}
          alt="SaveIcon" 
          className="image-button"
          style={{position:'absolute', top:'685px', left:'927px', zIndex:7}}
        />
        <img 
          src={require('./ExitIcon.png')} 
          alt="ExitIcon" 
          className="image-button"
          style={{position:'absolute', top:'766px', left:'927px', zIndex:7}}
          onClick={() => setEditing(false)}
        />
      </div>
    )
}

export default L8;