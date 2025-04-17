import React, { useState, useEffect, useRef } from 'react';

function L19({handlerestart}) {
    return(
      <div>
        <img src={require('./RegistrationError.png')} alt="RegistrationError" style={{position:'absolute', top:'69px', left:'216px', zIndex:13}}/>
        <img src={require('./RestartButton.png')} alt="RestartButton" style={{position:'absolute', top:'765px', left:'810px', zIndex:13}} onClick={handlerestart}/>
      </div>
    )
}

export default L19;