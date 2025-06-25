import React, { useState, useEffect, useRef } from 'react';

function L7({handledit, setReport, editable, leftCheckMark, rightCheckMark, recon, setPause}) {
    const imageMap = {
      1: require('./APStatusIcon.png'),
      2: require('./RcnSucceed.png'),
      3: require('./RcnFailed.png'),
      0: require('./OBStatusIcon.png'),
    };
  
    return(
      <div>
        <img src={require('./ImagingModeToolbar.png')} alt="Imaging Mode Toolbar" style={{position:'absolute', top:'458px', left:'921px', zIndex:7}}/>
        
        <img className="image-button"  src={require('./EditIcon.png')} alt="edit icon" style={{position:'absolute', top:'466px', left:'928px', zIndex:7}} onClick={handledit}/> 
        {!editable && <img src={require('./EditIconDis.png')} alt="edit icon dis" style={{position:'absolute', top:'466px', left:'928px', zIndex:7}}/>}
        <img className="image-button"  src={require('./ReportIcon.png')} alt="Report Icon" style={{position:'absolute', top:'547px', left:'928px', zIndex:7}} onClick={()=>{setReport(true)}}/>
        
        
        <>
        <img className="image-button" src={require('./PauseButtonBg.png')} alt="acquire icon" style={{position:'absolute', top:'659px', left:'921px', zIndex:7}}/>
        <img className="image-button"  src={require('./PauseButton.png')} alt="acquire icon" style={{position:'absolute', top:'664px', left:'926px', zIndex:7}} onClick={()=>{setPause(4)}}/>
        </>
        

        {/*Show icon based on backend param*/}
        {rightCheckMark!==null && (
          <img src={imageMap[rightCheckMark]} style={{ position: 'absolute', top: '860px', left: '1020px', zIndex: 7 }} alt="status icon" />
        )}
        {leftCheckMark!==null && (
          <img src={imageMap[leftCheckMark]} style={{ position: 'absolute', top: '860px', left: '815px', zIndex: 7 }} alt="status icon" />
        )}
        {recon!==null && (
          <img src={imageMap[recon]} style={{ position: 'absolute', top: '852px', left: '807px', zIndex: 7 }} alt="recon icon" />
        )}
      </div>
    )
}

export default L7;