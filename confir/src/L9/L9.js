import React, { useState, useEffect, useRef } from 'react';

function L9({error, measurements, handlepause, moveNext, stage, isCupReg, isTriReg, setExit}) {
    const shownext = (stage == 1 && moveNext) || (stage === 2 && isCupReg)
    useEffect(() => {
      if (shownext) {
          // Trigger the function after 10 seconds
          const timer = setTimeout(() => {
              handlepause(stage + 1);
          }, 60000); // 10000ms = 10 seconds

          // Cleanup timer if component unmounts or button disappears
          return () => clearTimeout(timer);
      }
  }, [shownext, stage]);


    return(
      <div>
        {/*isTriReg&&<img src={require('./ForwardNav Button.png')} alt="ForwardNav Button" style={{position:'absolute', top:'126px', left:'1622px', zIndex:9}} onClick={()=>setExit(true)}/>*/}
        {/*shownext&&<img src={require('./ForwardNav Button.png')} alt="ForwardNav Button" style={{position:'absolute', top:'126px', left:'1622px', zIndex:9}} onClick={()=>handlepause(stage+1)}/>*/}
        {(measurements || error)&&<>
          <img src={require('./Message1.png')} alt="Message1" style={{position:'absolute', top:'33px', left:'336px', zIndex:9}}/>
          <div style={{position:'absolute', top:'53px', left:'636px', zIndex:20, fontSize:'40px', color:'white', fontFamily:'Abel'}}>{measurements?measurements:error}°</div>
        </>}
        {(measurements && error)&&<>
          <img src={require('./Message2.png')} alt="Message2" style={{position:'absolute', top:'133px', left:'336px', zIndex:9}}/>
          <div style={{position:'absolute', top:'162px', left:'336px', zIndex:9}}>{error}</div>
        </>}
      </div>
    )
}

export default L9;