import React, { useState, useEffect, useRef } from 'react';

function L11({setReport, stage, setError}) {
  const [stitch, setStitch] = useState(null)
  const [localStage, setLocalStage] = useState(stage)
  const [imageNum, setImageNum] = useState(0)
  useEffect(() => {
      const fetchStitch = async () => {
        try {
          const response = await fetch(`http://localhost:5000/${imageNum === 0 ? 'stitch':'screenshot'}/${localStage}`);
          const data = await response.json();
          setStitch(data.img)
        } catch (error) {
          console.error('Error fetching states:', error);
          setError("Error connecting to server");
        }
      };
  
      fetchStitch();
      
    }, [localStage, imageNum]);
    const handleNext = () => {
      if(localStage === 0 && imageNum === 1){
          setLocalStage(1)
          setImageNum(2)
        } 

      else setImageNum(1)
    }
    const handlePrev = () => {
      if(localStage === 1){
        setImageNum(1)
        setLocalStage(0)
      }
      else setImageNum(0)
    }
    return(
      <div>
        <img src={require('../L10/BgBlur.png')} alt="ReportImageViewport" style={{position:'absolute', top:'0px', zIndex:10, aspectRatio:'1920/1080',height:'1080px'}}/>
        <img src={require('./ReportImageViewport.png')} alt="ReportImageViewport" style={{position:'absolute', top:'60px', left:'0px', zIndex:11}}/>
        
        <img src={stitch} style={{position:'absolute', width: '1920px', height:'960px', top:'60px', left:'0px', zIndex:11}}/>
        
        <img src={require('./DLReportButton.png')} alt="DLReportButton" style={{position:'absolute', top:'945px', left:'1744px', zIndex:11}}/>
        <img src={require('./ReportProgressBar.png')} alt="ReportProgressBar" style={{position:'absolute', top:'890px', left:'890px', zIndex:11}}/>
        <img className="image-button" src={require('./ReportReturnButton.png')} alt="ReportReturnButton" style={{position:'absolute', top:'981px', left:'415px', zIndex:11}} onClick={()=>{setReport(false)}}/>
        <img src={require('./ReportStageBar.png')} alt="ReportStageBar" style={{position:'absolute', top:'947px', left:'798px', zIndex:11}}/>
        
        <img className="image-button" src={require('./Hip1IconOn.png')} alt="Hip1IconOn" style={{position:'absolute', top:'962px', left:'808px', zIndex:11}} onClick={()=>{setLocalStage(0)}}/>
        {/*<img src={require('./Hip1IconOff.png')} alt="Hip1IconOff" style={{position:'absolute', top:'983px', left:'821px', zIndex:11}}/>*/}
        <img className="image-button" src={require('./CupIconOn.png')} alt="CupIconOn" style={{position:'absolute', top:'962px', left:'913px', zIndex:11}} onClick={()=>{setLocalStage(2)}}/>
        {/*<img src={require('./CupIconCompOff.png')} alt="CupIconCompOff" style={{position:'absolute', top:'971px', left:'924px', zIndex:11}}/>*/}
        <img className="image-button" src={require('./TrialIconOn.png')} alt="TrialIconOn" style={{position:'absolute', top:'978px', left:'1040px', zIndex:11}} onClick={()=>{setLocalStage(3)}}/>
        {/*<img src={require('./TrialIconCompOff.png')} alt="TrialIconCompOff" style={{position:'absolute', top:'962px', left:'1017px', zIndex:11}}/>*/}
        
        <img className="image-button" src={require('./ReportNextBtn.png')} alt="ReportNextBtn" style={{position:'absolute', top:'892px', left:'1087px', zIndex:11}} onClick={handleNext}/>
        <img className="image-button" src={require('./ReportPrevBtn.png')} alt="ReportPrevBtn" style={{position:'absolute', top:'892px', left:'833px', zIndex:11}} onClick={handlePrev}/>
        
        <img src={require('../L1/Logo.png')} alt="logo" style={{position:'absolute', top:'1041px', left:'13px', zIndex:11}}/>
        
      </div>
    )
}

export default L11;