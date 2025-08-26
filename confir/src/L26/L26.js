import React, { useState, useEffect, useRef } from 'react';

function L26({setSplash}) {
    const [waiting, setWaiting] = useState(true)

    useEffect(() => {
      const timer = setTimeout(() => {
        setWaiting(false)
      }, 3000)
      return () => clearTimeout(timer)
    },[])

    return(
      <div>
        <img src={require('./DisclaimerWindow.png')} style={{position:'absolute', top:'0px', zIndex:19, aspectRatio:'1920/1080',height:'1080px'}}/>
        <img className="image-button" src={require('../L23/ConfirmBtn.png')} alt="ConfirmBtn" style={{position:'absolute', top:'965px', left:'910px', zIndex:19}} onClick={()=> setSplash(false)}/>
        {waiting && <img src={require('./SplashWindow.png')} alt="SplashWindow" style={{position:'absolute', top:'0px', left:'0px', zIndex:19}}/>}
      </div>
    )
}

export default L26;