import React from 'react';
import './CircularProgress.css';
import backgroundImage from './LCBg.png';

const CircularProgress2 = () => {

  return (
    <div className="circular-progress">
      <img src={require('./L10/BgBlur.png')} alt="ReportImageViewport" style={{position:'absolute', top:'0px', zIndex:15, aspectRatio:'1920/1080', height:'1080px'}}/>
      <img src={backgroundImage} alt="window background" className="background-image" />
      <div className="image-container">
        <img
          src={require("./LoadingCircleNoPct.png")}
          alt="Rotating"
          className="rotating"
        />
      </div>

    </div>
  );
};

export default CircularProgress2;