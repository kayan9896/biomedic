import React, { useState, useEffect, useRef } from 'react';

function L17({handlerestart, setExit}) {
    const handleClose = () => {
      window.close()
    }
    return(
      <div>
        <img src={require('./ExitWindow.png')} alt="ExitWindow" style={{position:'absolute', top:'281px', left:'217px', zIndex:13}}/>
        <img src={require('./NewCaseBtn.png')} alt="NewCaseBtn" style={{position:'absolute', top:'522px', left:'640px', zIndex:13}} onClick={()=>{
          handlerestart()
          setExit(false)
        }}/>
        <img src={require('./CancelBtn.png')} alt="CancelBtn" style={{position:'absolute', top:'522px', left:'1330px', zIndex:13}} onClick={()=>setExit(false)}/>
        <img src={require('./SaveReportBtn.png')} alt="SaveReportBtn" style={{position:'absolute', top:'522px', left:'296px', zIndex:13}} />
        <img src={require('./ShutDownBtn.png')} alt="ShutDownBtn" style={{position:'absolute', top:'522px', left:'985px', zIndex:13}} onClick={handleClose}/>
      </div>
    )
}

export default L17;