import React, { useState, useEffect, useRef } from 'react';

function L19({handlerestart}) {
    return(
      <div>
        <img src={require('../L10/BgBlur.png')} style={{position:'absolute', top:'0px', zIndex:19, aspectRatio:'1920/1080',height:'1080px'}}/>
        <img src={require('./RegistrationError.png')} alt="RegistrationError" style={{position:'absolute', top:'69px', left:'216px', zIndex:19}}/>
        <img src={require('./RestartButton.png')} alt="RestartButton" style={{position:'absolute', top:'765px', left:'810px', zIndex:19}} onClick={handlerestart}/>
      </div>
    )
}

export default L19;