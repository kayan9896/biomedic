import React, { useState, useEffect, useRef } from 'react';

function L11({setReport, stage, setError}) {
  const [stitch, setStitch] = useState(null)
  const [localStage, setLocalStage] = useState(stage === 1 ? 0 : stage)
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
      console.log(localStage,imageNum)
      if(imageNum === 2) return
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
        <img src={require('./ReportImageViewport.png')} alt="ReportImageViewport" style={{position:'absolute', top:'0px', left:'0px', zIndex:11}}/>
        <img src={require('./ReportLabel.png')} alt="ReportLabel" style={{position:'absolute', top:'0px', left:'845px', zIndex:11}}/>
        <img src={require('./ReportBgBlur.png')} alt="ReportBgBlur" style={{position:'absolute', top:'0px', left:'0px', zIndex:10}}/>
        
        {stitch && <img src={stitch} style={{position:'absolute', width: '1920px', height:'960px', top:'0px', left:'0px', zIndex:11}}/>}
        
        
        <img className="image-button" src={require('./DLReportButton.png')} alt="DLReportButton" style={{position:'absolute', top:'1027px', left:'1280px', zIndex:11}}/>
        {localStage < 2 && imageNum === 0 && <img src={require('./RefStitch.png')} alt="RefStitch" style={{position:'absolute', top:'896px', left:'899px', zIndex:11}}/>}
        {localStage < 2 && imageNum === 1 && <img src={require('./RefVP1.png')} alt="RefVP1" style={{position:'absolute', top:'896px', left:'899px', zIndex:11}}/>}
        {localStage < 2 && imageNum === 2 && <img src={require('./RefVP2.png')} alt="RefVP2" style={{position:'absolute', top:'896px', left:'899px', zIndex:11}}/>}
        {localStage > 1 && imageNum === 1 && <img src={require('./CupVP.png')} alt="CupVP" style={{position:'absolute', top:'896px', left:'899px', zIndex:11}}/>}
        {localStage > 1 && imageNum === 0 && <img src={require('./CupStitch.png')} alt="CupStitch" style={{position:'absolute', top:'896px', left:'899px', zIndex:11}}/>}
        
        <img className="image-button" src={require('./ReportReturnButton.png')} alt="ReportReturnButton" style={{position:'absolute', top:'1027px', left:'516px', zIndex:11}} onClick={()=>{setReport(false)}}/>
        
        
        {(localStage === 0 || localStage === 1) && <img src={require('./HipIconOn.png')} alt="Hip1IconOn" style={{position:'absolute', top:'957px', left:'681px', zIndex:11}} />}
        <img className="image-button" src={require('./ReportHipIcon.png')} alt="ReportHipIcon" style={{position:'absolute', top:'984px', left:'766px', zIndex:12}} onClick={()=>{setLocalStage(0);setImageNum(0)}}/>
        {localStage === 2 && <img src={require('./CupIconOn.png')} alt="CupIconOn" style={{position:'absolute', top:'957px', left:'865px', zIndex:11}} />}
        <img className="image-button" src={require('./ReportCupIcon.png')} alt="ReportCupIcon" style={{position:'absolute', top:'970px', left:'916px', zIndex:12}} onClick={()=>{setLocalStage(2);setImageNum(0)}}/>
        {localStage === 3 && <img src={require('./TrialIconOn.png')} alt="TrialIconOn" style={{position:'absolute', top:'957px', left:'995px', zIndex:11}} />}
        <img className="image-button" src={require('./ReportTrialIcon.png')} alt="ReportTrialIcon" style={{position:'absolute', top:'980px', left:'1071px', zIndex:12}} onClick={()=>{setLocalStage(3);setImageNum(0)}}/>
        
        <img className="image-button" src={require('./ReportNextBtn.png')} alt="ReportNextBtn" style={{position:'absolute', top:'896px', left:'1036px', zIndex:11}} onClick={handleNext}/>
        <img className="image-button" src={require('./ReportPrevBtn.png')} alt="ReportPrevBtn" style={{position:'absolute', top:'896px', left:'843px', zIndex:11}} onClick={handlePrev}/>
        
      </div>
    )
}

export default L11;