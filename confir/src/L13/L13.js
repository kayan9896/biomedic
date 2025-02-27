import React, { useState, useEffect, useRef } from 'react';

function L13({handleConnect}) {
    return(
      <div>
        <img src={require('./SetupWindow.png')} alt="SetupWindow" style={{position:'absolute', top:'6px', left:'240px', zIndex:13}}/>
        <img src={require('./SetupTryAgain.png')} alt="SetupTryAgain" style={{position:'absolute', top:'826px', left:'995px', zIndex:13}}/>
        <img src={require('./SetupReturn.png')} alt="SetupReturn" style={{position:'absolute', top:'826px', left:'1330px', zIndex:13, cursor:'pointer'}} onClick={handleConnect}/>
        <img src={require('../L1/Logo.png')} style={{'position':'absolute', top:'1041px', left:'13px'}}/>
        <img src={require('../L2/ExitIcon.png')} style={{'position':'absolute', top:'1016px', left:'1853px'}}/>
      </div>
    )
}

export default L13;