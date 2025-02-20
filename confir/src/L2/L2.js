import React, { useState, useEffect, useRef } from 'react';

function L2({onInputChange,setShowKeyboard,onSelect,inputRef,pid}) {
    return(
        <>
        <img src={require('./Hip icon.png')} style={{'position':'absolute', top:'983px', left:'302px'}}/>
        <img src={require('./Vector 178.png')} style={{'position':'absolute', top:'983px', left:'427px'}}/>
        <img src={require('./Group 240.png')} style={{'position':'absolute', top:'983px', left:'552px'}}/>
        <img src={require('./NavMeasurementsSegment.png')} style={{'position':'absolute', top:'977px', left:'667px'}}/>
        <img src={require('./SetupIcon.png')} style={{'position':'absolute', top:'1016px', left:'1786px'}}/>
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