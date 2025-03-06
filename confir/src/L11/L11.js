import React, { useState, useEffect, useRef } from 'react';

function L11({setReport, stage, setError}) {
  const [stitch, setStitch] = useState(null)
  useEffect(() => {
      const fetchStitch = async () => {
        try {
          const response = await fetch(`http://localhost:5000/stitch/${stage}`);
          const data = await response.json();
          setStitch(data.img)
        } catch (error) {
          console.error('Error fetching states:', error);
          setError("Error connecting to server");
        }
      };
  
      fetchStitch();
      
    }, []);
    return(
      <div>
        <img src={require('../L10/BgBlur.png')} alt="ReportImageViewport" style={{position:'absolute', top:'0px', zIndex:10}}/>
        <img src={require('./ReportImageViewport.png')} alt="ReportImageViewport" style={{position:'absolute', top:'60px', left:'0px', zIndex:11}}/>
        <img src={stitch} style={{position:'absolute', width: '1920px', height:'960px', top:'60px', left:'0px', zIndex:11}}/>
        <img src={require('./DLReportButton.png')} alt="DLReportButton" style={{position:'absolute', top:'945px', left:'1744px', zIndex:11}}/>
        <img src={require('./ReportProgressBar.png')} alt="ReportProgressBar" style={{position:'absolute', top:'890px', left:'833px', zIndex:11}}/>
        <img src={require('./ReportReturnButton.png')} alt="ReportReturnButton" style={{position:'absolute', top:'987px', left:'415px', zIndex:11}} onClick={()=>{setReport(false)}}/>
        <img src={require('./ReportStageBar.png')} alt="ReportStageBar" style={{position:'absolute', top:'947px', left:'798px', zIndex:11}}/>
        <img src={require('../L1/Logo.png')} alt="logo" style={{position:'absolute', top:'1041px', left:'13px', zIndex:11}}/>
        
      </div>
    )
}

export default L11;