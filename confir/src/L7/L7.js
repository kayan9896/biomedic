import React, { useState, useEffect, useRef } from 'react';

function L7({setEditing, setReport, leftCheckMark, rightCheckMark}) {
    return(
      <div>
        <img src={require('./ImagingModeToolbar.png')} alt="Imaging Mode Toolbar" style={{position:'absolute', top:'458px', left:'921px', zIndex:7}}/>
        <img src={require('./AcquireImageIcon.png')} alt="acquire icon" style={{position:'absolute', top:'660px', left:'899px', zIndex:7}}/>
        <img src={require('./EditIcon.png')} alt="edit icon" style={{position:'absolute', top:'466px', left:'928px', zIndex:7}} onClick={()=>{setEditing('left')}}/>
        <img src={require('./ReportIcon.png')} alt="Report Icon" style={{position:'absolute', top:'547px', left:'928px', zIndex:7}} onClick={()=>{setReport(true)}}/>
        {/*Show icon based on backend param*/}
        {rightCheckMark!==null && (rightCheckMark == 1? <img src={require('./APStatusIcon.png')} style={{position:'absolute', top:'857px', left:'1019px', zIndex:7}}/>:
        (rightCheckMark ==2? <img src={require('./RcnCheckmark.png')} style={{position:'absolute', top:'857px', left:'1019px', zIndex:7}}/>:
        (rightCheckMark==3? <img src={require('./RecFailedIcon.png')} style={{position:'absolute', top:'857px', left:'1019px', zIndex:7}}/> : 
      <img src={require('./OBStatusIcon.png')} style={{position:'absolute', top:'857px', left:'1019px', zIndex:7}}/>))
      )}
        {leftCheckMark!==null && (leftCheckMark == 1 ? <img src={require('./APStatusIcon.png')} alt="AP Status Icon" style={{position:'absolute', top:'860px', left:'816px', zIndex:7}}/> :
        (leftCheckMark ==2? <img src={require('./RcnCheckmark.png')} style={{position:'absolute', top:'860px', left:'816px', zIndex:7}}/>:
        (leftCheckMark==3? <img src={require('./RecFailedIcon.png')} style={{position:'absolute', top:'860px', left:'816px', zIndex:7}}/> : 
      <img src={require('./OBStatusIcon.png')} style={{position:'absolute', top:'860px', left:'816px', zIndex:7}}/>))
      )}
      </div>
    )
}

export default L7;