import React, { useState, useEffect, useRef } from 'react';

function L17({handlerestart, setExit}) {
    const handleClose = () => {
      window.close()
    }
    return(
      <div>
        <img src={require('../L10/BgBlur.png')} style={{position:'absolute', top:'0px', zIndex:17, aspectRatio:'1920/1080',height:'1080px'}}/>
        <img src={require('./ExitWindow.png')} alt="ExitWindow" style={{position:'absolute', top:'358px', left:'498px', zIndex:17}}/>
        <img className="image-button" src={require('./NewCaseBtn.png')} alt="NewCaseBtn" style={{position:'absolute', top:'539px', left:'785px', zIndex:17}} onClick={()=>{
          handlerestart()
          setExit(false)
        }}/>
        <img className="image-button" src={require('../L23/NoBtn.png')} alt="CancelBtn" style={{position:'absolute', top:'539px', left:'1241px', zIndex:17}} onClick={()=>setExit(false)}/>
        <img className="image-button" src={require('./SaveReportBtn.png')} alt="SaveReportBtn" style={{position:'absolute', top:'539px', left:'557px', zIndex:17}} />
        <img className="image-button" src={require('./ShutDownBtn.png')} alt="ShutDownBtn" style={{position:'absolute', top:'539px', left:'1013px', zIndex:17}} onClick={handleClose}/>
      </div>
    )
}

export default L17;