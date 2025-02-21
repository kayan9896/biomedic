import React, { useState, useEffect, useRef } from 'react';

function L9({error, measurements, setPause}) {
    return(
      <div>
        <img src={require('./BackNavButton.png')} alt="BackNavButton" style={{position:'absolute', top:'126px', left:'298px', zIndex:9}}/>
        <img src={require('./ForwardNav Button.png')} alt="ForwardNav Button" style={{position:'absolute', top:'126px', left:'1622px', zIndex:9}} onClick={()=>{setPause(true)}}/>
        <img src={require('./Message1.png')} alt="Message1" style={{position:'absolute', top:'33px', left:'336px', zIndex:9}}/>
        <img src={require('./Message2.png')} alt="Message2" style={{position:'absolute', top:'33px', left:'336px', zIndex:9}}/>
      </div>
    )
}

export default L9;