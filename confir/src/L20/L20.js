import React, { useState, useEffect, useRef } from 'react';

function L20({image, setShowglyph}) {
    return(
      <div>
        <img src={require('../L10/BgBlur.png')} style={{position:'absolute', top:'0px', zIndex:20, aspectRatio:'1920/1080',height:'1080px'}}/>
        <img src={require('./C-armReferenceNotDetected.png')} alt="FrameAnalysisError" style={{position:'absolute', top:'70px', left:'216px', zIndex:20}}/>
        <img src={image} style={{position:'absolute', top:'236px', left:'1101px', width: '500px', height:'500px', zIndex:20}}/>
        <img src={require('./ReturnButton.png')} className="image-button" style={{position:'absolute', top:'765px', left:'1307px', zIndex:20}} onClick={()=>{setShowglyph(false)}}/>
      </div>
    )
}

export default L20;