import React, { useState, useEffect, useRef } from 'react';

function L6({editableSide, setEditing, hasAp, hasOb}) {

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
        {editableSide === 'right' && <img src={hasAp ? require('./EditModeBGBlur.png') : require('./EditModeBGBlurWithoutText.png')} alt="EditModeBGBlur" style={{width: '100%', height: '100%'}} onClick={()=>{hasAp ? setEditing('left') : setEditing('right')}}/>}
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
        {editableSide === 'left' && <img src={hasOb ? require('./EditModeBGBlur.png') : require('./EditModeBGBlurWithoutText.png')} alt="EditModeBGBlur" style={{width: '100%', height: '100%'}} onClick={()=>{hasOb ? setEditing('right') : setEditing('left')}}/>}
      </div>
    </>
    )
}

export default L6;