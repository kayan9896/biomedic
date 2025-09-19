import React, { useState, useEffect, useRef } from 'react';

function L9({error, measurements, handlepause, moveNext, stage, isCupReg, isTriReg, setExit, takeAP}) {
    const shownext = (stage == 1 && moveNext) || (stage === 2 && moveNext)
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
    const tb = {
      '114': ['Failed to autodetect image landmarks', 'Edit or retake'],
      '115': ['Wrong side hip detected', 'Retake'],
      '120': ['Failed hemi-pelvis reconstruction', 'Edit or retake'], 
      '121': ['Failed proximal femur reconstruction', 'Edit or retake'], 
      '122': ['Failed cup reconstruction', 'Edit or retake'], 
      '129': ['Failed reconstruction - mismatched sides', 'Edit or retake'],
      '131': ['Failed Cup Registration','Retake'],
      '132': ['Failed Trial Analysis Registration','Retake'],
    }
    const errortext = error in tb ? tb[error] : []


    return(
      <div>
        {/*isTriReg&&<img src={require('./ForwardNav Button.png')} alt="ForwardNav Button" style={{position:'absolute', top:'126px', left:'1622px', zIndex:9}} onClick={()=>setExit(true)}/>*/}
        {/*shownext&&<img src={require('./ForwardNav Button.png')} alt="ForwardNav Button" style={{position:'absolute', top:'126px', left:'1622px', zIndex:9}} onClick={()=>handlepause(stage+1)}/>*/}
        {measurements &&<>
          <img src={require('./Message1.png')} alt="Message1" style={{position:'absolute', top:'33px', left:'336px', zIndex:9}}/>
          <img src={require('./Message2.png')} alt="Message2" style={{position:'absolute', top:'133px', left:'336px', zIndex:9}}/>
          
          <div style={{position: 'absolute', display: 'flex', flexDirection: 'row', justifyContent:'space-evenly', top:'33px', left: '336px', width: '1249px', height: '200px', zIndex: 9}}>
          {Object.keys(measurements).map((column, i) => {
            return (
              <div key={i} style={{display: 'flex', flexDirection: 'column', textAlign:'center', color: 'white', fontFamily:'abel', justifyContent:'space-evenly'}}>
                <div style={{fontSize: '75px', color:'white', textDecorationLine:'underline', textDecorationThickness:'2.5px', textUnderlineOffset: '5px'}}>{column}</div>
                {measurements[column].includes('mm') ? (
                  <div style={{display: 'flex', flexDirection: 'row', justifyContent:'center'}}>
                    <text style={{fontSize: '75px'}}>{measurements[column].split('mm')[0]}</text>
                    <div style={{fontSize: '40px'}}>mm</div>
                  </div>
             ) : 
                <text style={{fontSize: '75px'}}>{measurements[column]}°</text>}
              </div>
            )
          })}
        </div>
        </>}
        {(errortext[0])&&<>
          <img src={require('./Message1.png')} alt="Message1" style={{position:'absolute', top:'33px', left:'336px', zIndex:9}}/>
          <div style={{position:'absolute', display:'flex', flexDirection:'column', justifyContent:'center', textAlign:'center', top:'33px', left: '336px', width: '1249px', height: '100px', zIndex:9, fontSize:'75px', color:'white', fontFamily:'Abel'}}>{errortext[0]}</div>
        </>}
        {(errortext[1])&&<>
          <img src={require('./Message2.png')} alt="Message2" style={{position:'absolute', top:'133px', left:'336px', zIndex:9}}/>
          <div style={{position:'absolute', display:'flex', flexDirection:'column', justifyContent:'center', textAlign:'center', top:'133px', left: '336px', width: '1249px', height: '100px', zIndex:9, fontSize:'75px', color:'#26A742', fontFamily:'Abel'}}>{errortext[1]}</div>
        </>}
        {takeAP&&<>
          <img src={require('./Message2.png')} alt="Message2" style={{position:'absolute', top:'133px', left:'336px', zIndex:9}}/>
          <div style={{position:'absolute', display:'flex', flexDirection:'column', justifyContent:'center', textAlign:'center', top:'133px', left: '336px', width: '1249px', height: '100px', zIndex:9, fontSize:'75px', color:'#26A742', fontFamily:'Abel'}}>{takeAP}</div>
        </>}
      </div>
    )
}

export default L9;