import React, { useState, useEffect, useRef } from 'react';

function L26({txt, setGe}) {

    return(
      <div>
        <img src={require('../L10/BgBlur.png')} style={{position:'absolute', top:'0px', zIndex:18, aspectRatio:'1920/1080',height:'1080px'}}/>
        <img src={require('./GEwindowBg.png')} alt="GEwindowBg" style={{position:'absolute', top:'358px', left:'612px', zIndex:18}}/>
        {txt !== 'Saved!' && <div style={{position:'absolute', top:'375px', left:'704px', width: '512px', height:'46px', zIndex:18, color:'white', fontFamily:'abel', fontSize:'38px', textAlign:'center'}}>Error</div>}
        <div style={{position:'absolute', top:'432px', left:'764px', width: '498px', height:'87px', zIndex:18, color:'white', fontFamily:'abel', fontSize:'23px'}}>{txt}</div>
        <img className="image-button" src={require('./OkBtn.png')} alt="OkBtn" style={{position:'absolute', top:'539px', left:'898px', zIndex:18}} onClick={()=>setGe(false)}/>
        
      </div>
    )
}

export default L26;