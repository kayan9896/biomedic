import React, { useState, useEffect } from 'react';
import './App.css';

function Livecam() {
    const [streamActive, setStreamActive] = useState(false);
    function startStream(){
        setStreamActive(true);
      };
    
      function stopStream(){
        setStreamActive(false);
      };
    return(
    <div className='App'>
        <div className="controls">
        <button onClick={startStream}>Start Stream</button>
        <button onClick={stopStream}>Stop Stream</button>
    </div>
    {streamActive && (
        <div className="video-container">
        <img
            src="http://localhost:5000/video_feed"
            alt="Camera Stream"
            style={{ maxWidth: '100%', height: 'auto' }}
        />
        </div>
    )}
    </div>
  )
}

export default Livecam;