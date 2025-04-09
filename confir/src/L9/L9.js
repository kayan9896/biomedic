import React, { useState, useEffect, useRef } from 'react';

function L9({error, measurements, handlepause, moveNext, stage}) {
    return(
      <div>

        {stage!==0&&moveNext&&<img src={require('./ForwardNav Button.png')} alt="ForwardNav Button" style={{position:'absolute', top:'126px', left:'1622px', zIndex:9}} onClick={handlepause}/>}
        {(measurements || error)&&<>
          <img src={require('./Message1.png')} alt="Message1" style={{position:'absolute', top:'33px', left:'336px', zIndex:19}}/>
          <div style={{position:'absolute', top:'53px', left:'636px', zIndex:20, fontSize:'40px', color:'white', fontFamily:'Abel'}}>{measurements?measurements:error}°</div>
        </>}
        {(measurements && error)&&<>
          <img src={require('./Message2.png')} alt="Message2" style={{position:'absolute', top:'162px', left:'336px', zIndex:19}}/>
          <div style={{position:'absolute', top:'162px', left:'336px', zIndex:20}}>{error}</div>
        </>}
      </div>
    )
}

export default L9;