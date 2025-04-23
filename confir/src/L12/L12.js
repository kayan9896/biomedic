import React, { useState, useEffect, useRef } from 'react';

function L12({pause, setPause, setReport, handlenext}) {
  const [next, setNext] = useState(null)
  if(pause === 1)
    return(
      <div>
        <img src={require('./PauseWindow.png')} alt="PauseWindow" style={{position:'absolute', top:'77px', left:'217px', zIndex:10}}/>
        <img src={require('./ResumeButton.png')} alt="ResumeButton" style={{position:'absolute', top:'764px', left:'815px', zIndex:10, cursor:'pointer'}} onClick={()=>setPause(0)}/>
      </div>
    )
  if(pause === 2)
    return(
      <div>
        <img src={require('./SelectWindow.png')} alt="SelectWindow" style={{position:'absolute', top:'77px', left:'217px', zIndex:10}}/>
        <img src={require('./DeselectedCup.png')} alt="DeselectedCup" style={{position:'absolute', top:'368px', left:'536px', zIndex:10}} onClick={()=>setNext('next')}/>
        {next==='next'&&<img src={require('./SelectedCup.png')} alt="SelectedCup" style={{position:'absolute', top:'368px', left:'536px', zIndex:10}} />}
        <img src={require('./DeselectedTrial.png')} alt="DeselectedTrial" style={{position:'absolute', top:'368px', left:'1009px', zIndex:10}} onClick={()=>setNext('skip')}/>
        {next==='skip'&&<img src={require('./SelectedTrial.png')} alt="SelectedTrial" style={{position:'absolute', top:'368px', left:'1009px', zIndex:10}} />}
        <img src={require('./GoBackButton.png')} alt="GoBackButton" style={{position:'absolute', top:'765px', left:'267px', zIndex:10}} onClick={()=>setPause(0)}/>
        <img src={require('./ContinueButton.png')} alt="ContinueButton" style={{position:'absolute', top:'765px', left:'1359px', zIndex:10, cursor:'pointer'}} onClick={() =>{
          handlenext(next)
        }}/>
        {!next&&<img src={require('./DisableContinueButton.png')} alt="DisableContinueButton" style={{position:'absolute', top:'765px', left:'1359px', zIndex:10}}/>}
      </div>
    )
  if(pause === 3)
    return(
      <div>
        <img src={require('./TrialPauseWindow.png')} alt="TrialPauseWindow" style={{position:'absolute', top:'77px', left:'217px', zIndex:10}}/>
        <img src={require('./GoBackButton.png')} alt="GoBackButton" style={{position:'absolute', top:'765px', left:'267px', zIndex:10}} onClick={()=>setPause(0)}/>
        <img src={require('./ContinueButton.png')} alt="ContinueButton" style={{position:'absolute', top:'765px', left:'1359px', zIndex:10, cursor:'pointer'}} onClick={() =>{
          handlenext('next')
        }}/>
      </div>
    )
  if(pause === 10)
    return(
      <div>
        <img src={require('../L10/BgBlur.png')} alt="ReportImageViewport" style={{position:'absolute', top:'0px', zIndex:10}}/>
        <img src={require('./RefPauseWindow.png')} alt="RefPauseWindow" style={{position:'absolute', top:'77px', left:'217px', zIndex:10}}/>
        <img src={require('./ContinueButton.png')} alt="ContinueButton" style={{position:'absolute', top:'765px', left:'1359px', zIndex:10, cursor:'pointer'}} onClick={()=>{
          setPause(0)
        }}/>
      </div>
    )
}

export default L12;