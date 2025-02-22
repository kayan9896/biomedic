import React, { useState, useEffect, useRef } from 'react';

function L13({handleConnect}) {
    return(
      <div>
        <img src={require('./SetupWindow.png')} alt="SetupWindow" style={{position:'absolute', top:'6px', left:'240px', zIndex:13}}/>
        <img src={require('./SetupTryAgain.png')} alt="SetupTryAgain" style={{position:'absolute', top:'826px', left:'995px', zIndex:13}}/>
        <img src={require('./SetupReturn.png')} alt="SetupReturn" style={{position:'absolute', top:'826px', left:'1330px', zIndex:13, cursor:'pointer'}} onClick={handleConnect}/>
      </div>
    )
}

export default L13;