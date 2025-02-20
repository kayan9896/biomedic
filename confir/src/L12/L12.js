import React, { useState, useEffect, useRef } from 'react';

function L12({setPause, setReport, handlenext}) {
    return(
      <div>
        <img src={require('./PauseWindow.png')} alt="PauseWindow" style={{position:'absolute', top:'87px', left:'232px', zIndex:10}}/>
        <img src={require('./GoBackButton.png')} alt="GoBackButton" style={{position:'absolute', top:'765px', left:'263px', zIndex:10}} onClick={()=>{setReport(setPause)}}/>
        <img src={require('./ViewReportButton.png')} alt="ViewReportButton" style={{position:'absolute', top:'765px', left:'813px', zIndex:10, cursor:'pointer'}} onClick={()=>{setReport(true)}}/>
        <img src={require('./ContinueButton.png')} alt="ContinueButton" style={{position:'absolute', top:'765px', left:'1359px', zIndex:10, cursor:'pointer'}} onClick={handlenext}/>
      </div>
    )
}

export default L12;