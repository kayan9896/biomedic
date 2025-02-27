import React, { useState, useEffect, useRef } from 'react';

function L2({onInputChange,setShowKeyboard,onSelect,inputRef,pid,setSetting,setting,stage}) {
    return(
        <>
        {stage>1?<img src={require('./HipIcon3.png')} style={{'position':'absolute', top:'983px', left:'302px'}}/>:(
          stage===0?<img src={require('./HipIcon1.png')} style={{'position':'absolute', top:'983px', left:'302px'}}/>:
          <img src={require('./HipIcon2.png')} style={{'position':'absolute', top:'983px', left:'302px'}}/>
        )}
        {stage<2?<img src={require('./CupIcon1.png')} style={{'position':'absolute', top:'983px', left:'427px'}}/>:(
          stage===2?<img src={require('./CupIcon2.png')} style={{'position':'absolute', top:'983px', left:'427px'}}/>:
          <img src={require('./CupIcon3.png')} style={{'position':'absolute', top:'983px', left:'427px'}}/>
        )}
        {stage<3?<img src={require('./TrialIcon1.png')} style={{'position':'absolute', top:'983px', left:'552px'}}/>:
        <img src={require('./TrialIcon2.png')} style={{'position':'absolute', top:'983px', left:'552px'}}/>
        }
        <img src={require('./NavMeasurementsSegment.png')} style={{'position':'absolute', top:'977px', left:'667px'}}/>
        <img src={require('./SetupIcon.png')} style={{'position':'absolute', top:'1016px', left:'1786px'}} onClick={()=>{setSetting(!setting)}}/>
        <img src={require('./ExitIcon.png')} style={{'position':'absolute', top:'1016px', left:'1853px'}}/>
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