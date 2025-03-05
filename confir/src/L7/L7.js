import React, { useState, useEffect, useRef } from 'react';

function L7({setEditing, setReport, leftCheckMark, rightCheckMark}) {
    const imageMap = {
      1: require('./APStatusIcon.png'),
      2: require('./RcnCheckmark.png'),
      3: require('./RecFailedIcon.png'),
      0: require('./OBStatusIcon.png'),
    };
  
    return(
      <div>
        <img src={require('./ImagingModeToolbar.png')} alt="Imaging Mode Toolbar" style={{position:'absolute', top:'458px', left:'921px', zIndex:7}}/>
        <img src={require('./AcquireImageIconBg.png')} alt="acquire icon" style={{position:'absolute', top:'659px', left:'899px', zIndex:7}}/>
        <img className="image-button"  src={require('./AcquireImageIcon.png')} alt="acquire icon" style={{position:'absolute', top:'667px', left:'907px', zIndex:7}}/>
        <img className="image-button"  src={require('./EditIcon.png')} alt="edit icon" style={{position:'absolute', top:'466px', left:'928px', zIndex:7}} onClick={()=>{setEditing('left')}}/>
        <img className="image-button"  src={require('./ReportIcon.png')} alt="Report Icon" style={{position:'absolute', top:'547px', left:'928px', zIndex:7}} onClick={()=>{setReport(true)}}/>
        {/*Show icon based on backend param*/}
        {rightCheckMark && (
          <img src={imageMap[rightCheckMark]} style={{ position: 'absolute', top: '857px', left: '1019px', zIndex: 7 }} alt="status icon" />
        )}
        {leftCheckMark && (
          <img src={imageMap[leftCheckMark]} style={{ position: 'absolute', top: '860px', left: '816px', zIndex: 7 }} alt="status icon" />
        )}
      </div>
    )
}

export default L7;