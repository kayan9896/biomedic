import React, { useState, useEffect, useRef } from 'react';

function L11({setReport}) {
    return(
      <div>
        <img src={require('./ReportImageViewport.png')} alt="ReportImageViewport" style={{position:'absolute', top:'60px', left:'0px', zIndex:11}}/>
        <img src={require('./DLReportButton.png')} alt="DLReportButton" style={{position:'absolute', top:'945px', left:'1744px', zIndex:11}}/>
        <img src={require('./ReportProgressBar.png')} alt="ReportProgressBar" style={{position:'absolute', top:'890px', left:'833px', zIndex:11}}/>
        <img src={require('./ReportReturnButton.png')} alt="ReportReturnButton" style={{position:'absolute', top:'987px', left:'415px', zIndex:11}} onClick={()=>{setReport(false)}}/>
        <img src={require('./ReportStageBar.png')} alt="ReportStageBar" style={{position:'absolute', top:'947px', left:'798px', zIndex:11}}/>
        <img src={require('../L1/Logo.png')} alt="logo" style={{position:'absolute', top:'1041px', left:'13px', zIndex:11}}/>
      </div>
    )
}

export default L11;