import React, { useState, useEffect, useRef } from 'react';

function L2({onInputChange,setShowKeyboard,onSelect,inputRef,pid,setSetting,setExit,stage,setStage,moveNext,handlerestart,handlenext,isCupReg,showCarmBox}) {
  const clickDash = () => {
    if(stage === 0){
      if(moveNext) handlenext()
    }
    if(stage === 1){
      if(!moveNext) handlerestart()
    }
    if(stage === 2){
      handlenext()
    }
    if(stage === 3){
      handlenext(false)
    }
  }

  const blueStage = (stage) =>{
    if(stage === 0) return {'position':'absolute', top:'983px', left:'293px'}
    if(stage === 1) return {'position':'absolute', top:'983px', left:'381px'}
    if(stage === 2) return {'position':'absolute', top:'983px', left:'476px'}
    if(stage === 3) return {'position':'absolute', top:'983px', left:'571px'}
  }
  const showDash = (stage) => {
    if(stage === 0){
      if(moveNext) return [1, {'position':'absolute', top:'983px', left:'381px'}]
      return [null, null]
    }
    if (stage === 1){
      if(moveNext) return [null, null]
      return [0, {'position':'absolute', top:'983px', left:'293px'}]
    }
    if(stage === 2){
      if(moveNext) return [null, null]
      return [3, {'position':'absolute', top:'983px', left:'571px'}]
    }
    if(stage === 3){
      if(moveNext) return [null, null]
      return [2, {'position':'absolute', top:'983px', left:'476px'}]
    }
  }
    return(
      <>
        <img src={require('./CurrentStageBg.png')} style={blueStage(stage)}/>
        {showDash(stage)[0]!==null&&!showCarmBox&&<img src={require('./PossibleStageBg.png')} style={showDash(stage)[1]} onClick={clickDash}/>}

        {(
          stage===0&&!moveNext?<img src={require('./HipIcon1.png')} style={{'position':'absolute', width:'54px', height:'75px', top:'988px', left:'319px', pointerEvents:'none'}}/>:
          <img src={require('./HipIcon2.png')} style={{'position':'absolute', width:'54px', height:'75px', top:'988px', left:'319px', pointerEvents:'none'}}/>
        )}
        {(
          stage===0||(stage===1&&!moveNext)?<img src={require('./HipIcon3.png')} style={{'position':'absolute', width:'54px', height:'75px', top:'988px', left:'385px', pointerEvents:'none'}}/>:
          <img src={require('./HipIcon4.png')} style={{'position':'absolute', width:'54px', height:'75px', top:'988px', left:'385px', pointerEvents:'none'}}/>
        )}
        {(
          isCupReg?<img src={require('./CupIcon2.png')} style={{'position':'absolute', width:'75px', height:'75px', top:'988px', left:'483px', pointerEvents:'none'}}/>:
          <img src={require('./CupIcon1.png')} style={{'position':'absolute', width:'75px', height:'75px', top:'988px', left:'483px', pointerEvents:'none'}}/>
        )}
        {(stage===3&&moveNext)?<img src={require('./TrialIcon2.png')} style={{'position':'absolute', width:'63px', height:'67px', top:'992px', left:'584px', pointerEvents:'none'}}/>:
        <img src={require('./TrialIcon1.png')} style={{'position':'absolute', width:'63px', height:'67px', top:'992px', left:'584px', pointerEvents:'none'}}/>
        }
        <img src={require('./NavMeasurementsSegment.png')} style={{'position':'absolute', top:'977px', left:'667px'}}/>
        <img src={require('./SettingIcon.png')} style={{'position':'absolute', top:'1016px', left:'1786px'}} onClick={()=>{setSetting(true)}}/>
        <img src={require('./ExitIcon.png')} style={{'position':'absolute', top:'1016px', left:'1853px'}} onClick={()=>{setExit(true)}}/>
        <input
        ref={inputRef}
        type="text"
        value={pid}
        onChange={onInputChange}
        onClick={() => setShowKeyboard(true)}
        onSelect={onSelect}
        style={{
          position: 'absolute',
          left: '66px',
          top: '988px',
          width: '170px',
          background: 'transparent',
          color: 'white',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          border: '0px solid',
          padding: '8px',
          fontSize: '16px'
        }}
        placeholder="no patient data"
      />
        </>
    )
}

export default L2;