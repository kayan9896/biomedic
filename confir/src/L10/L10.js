import React, { useState, useEffect, useRef } from 'react';

function L10({angle,rotationAngle}) {
    return(
      <>
      <img src={require('./BgBlur.png')} alt="ReportImageViewport" style={{position:'absolute', zIndex:10}}/>
      <div style={{position:'absolute', top:'82px', left:'337px', zIndex:10}}>
        <img src={require('../carmbox.png')} alt="box" />
        <div className="hand" style={{ 
          transform: `rotate(${angle}deg)`,
          position:'absolute', 
          top:'224px', 
          left:'298px', 
          zIndex:'11' 
        }}>
          <img src={require('../tiltcarm.png')} alt="indicator" />
        </div>
        <div className="hand" style={{ 
          transform: `rotate(${rotationAngle}deg)`,
          position:'absolute', 
          top:'220px', 
          left:'750px', 
          zIndex:'11' 
        }}>
          <img src={require('../rotcarm.png')} alt="indicator" />
        </div>
      </div>
      
      </>
    )
}

export default L10;