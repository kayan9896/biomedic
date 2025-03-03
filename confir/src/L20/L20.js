import React, { useState, useEffect, useRef } from 'react';

function L20({image, setShowglyph}) {
    return(
      <div>
        <img src={require('./FrameAnalysisError.png')} alt="FrameAnalysisError" style={{position:'absolute', top:'70px', left:'216px', zIndex:13}}/>
        <img src={image} style={{position:'absolute', top:'150px', left:'1050px', width: '600px', height:'600px', zIndex:13}} onClick={()=>{setShowglyph(false)}}/>
      </div>
    )
}

export default L20;