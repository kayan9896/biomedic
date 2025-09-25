import React, { useState, useEffect, useRef } from 'react';

function L18({handleDl, setUsb}) {

    return(
      <div>
        <img src={require('../L10/BgBlur.png')} style={{position:'absolute', top:'0px', zIndex:18, aspectRatio:'1920/1080',height:'1080px'}}/>
        <img src={require('./FlashDriveNotDetectedWindow.png')} alt="FlashDriveNotDetectedWindow" style={{position:'absolute', top:'233px', left:'612px', zIndex:18}}/>
        
        <img className="image-button" src={require('./CancelBtnforFlashDrive.png')} alt="CancelBtn" style={{position:'absolute', top:'663px', left:'1016px', zIndex:18}} onClick={()=>setUsb(false)}/>
        <img className="image-button" src={require('./SaveReportBtn.png')} alt="SaveReportBtn" style={{position:'absolute', top:'663px', left:'718px', zIndex:18}} onClick={()=>{
          handleDl();
          setUsb(false)
        }}/>
      </div>
    )
}

export default L18;