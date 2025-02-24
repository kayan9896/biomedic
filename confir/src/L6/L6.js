import React, { useState, useEffect, useRef } from 'react';

function L6({editableSide, setEditing}) {

    return(
      <>
      {/* Left side */}
      <div 
        style={{
          position: 'absolute',
          top: '0px',
          left: '0px',
          width: '960px',
          height: '960px',
          zIndex: 6,
          pointerEvents: editableSide === 'left' ? 'none' : 'auto'
        }}
      >
        {editableSide === 'right' && <img src={require('./EditModeBGBlur.png')} alt="EditModeBGBlur" style={{width: '100%', height: '100%'}} onClick={()=>{setEditing('left')}}/>}
      </div>
      
      {/* Right side */}
      <div 
        style={{
          position: 'absolute',
          top: '0px',
          left: '960px',
          width: '960px',
          height: '960px',
          zIndex: 6,
          pointerEvents: editableSide === 'right' ? 'none' : 'auto'
        }}
      >
        {editableSide === 'left' && <img src={require('./EditModeBGBlur.png')} alt="EditModeBGBlur" style={{width: '100%', height: '100%'}} onClick={()=>{setEditing('right')}}/>}
      </div>
    </>
    )
}

export default L6;