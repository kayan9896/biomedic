import React, { useState, useEffect, useRef } from 'react';

function L24({setSplash}) {
    const [waiting, setWaiting] = useState(true)

    useEffect(() => {
      const timer = setTimeout(() => {
        setWaiting(false)
      }, 3000)
      return () => clearTimeout(timer)
    },[])

    return(
      <div>
        <img src={require('./DisclaimerWindow.png')} style={{position:'absolute', top: '40px', left:'36px', zIndex:19}}/>
        <img className="image-button" src={require('./ConfirmBtn.png')} alt="ConfirmBtn" style={{position:'absolute', top:'911px', left:'834px', zIndex:19}} onClick={()=> setSplash(false)}/>
        {waiting && <img src={require('./SplashWindow.png')} alt="SplashWindow" style={{position:'absolute', top:'0px', left:'0px', zIndex:19}}/>}
      </div>
    )
}

export default L24;