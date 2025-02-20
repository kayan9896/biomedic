import React, { useState, useEffect, useRef } from 'react';

function L7({setEditing, setReport}) {
    return(
      <div>
        <img src={require('./ImagingModeToolbar.png')} alt="Imaging Mode Toolbar" style={{position:'absolute', top:'458px', left:'921px', zIndex:7}}/>
        <img src={require('./AcquireImageIcon.png')} alt="acquire icon" style={{position:'absolute', top:'660px', left:'899px', zIndex:7}}/>
        <img src={require('./EditIcon.png')} alt="edit icon" style={{position:'absolute', top:'466px', left:'928px', zIndex:7}} onClick={()=>{setEditing(true)}}/>
        <img src={require('./ReportIcon.png')} alt="Report Icon" style={{position:'absolute', top:'547px', left:'928px', zIndex:7}} onClick={()=>{setReport(true)}}/>
        {/*Show icon based on backend param*/}
        <img src={require('./OBStatusIcon.png')} alt="OB Status Icon" style={{position:'absolute', top:'857px', left:'1019px', zIndex:7}}/>
        <img src={require('./APStatusIcon.png')} alt="AP Status Icon" style={{position:'absolute', top:'860px', left:'816px', zIndex:7}}/>
      </div>
    )
}

export default L7;