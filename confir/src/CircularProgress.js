import React from 'react';
import './CircularProgress.css';
import backgroundImage from './LCBg.png';

const CircularProgress = ({ percentage }) => {
  const radiusOuter = 103;
  const radiusInner = 95;
  const circumference = 2 * Math.PI * radiusOuter;
  const offset = circumference - (percentage / 100) * circumference;

  // Gradient colors
  const gradientColors = [
    '#00B0F0', // tail (start)
    '#00B0F0', // head (end)
  ];

  return (
    <div className="circular-progress">
      <img src={require('./L10/BgBlur.png')} alt="ReportImageViewport" style={{position:'absolute', top:'0px', zIndex:10}}/>
      <img src={backgroundImage} alt="window background" className="background-image" />
      <svg width="1920" height="960" viewBox="0 0 1920 960">
        <defs>
          <linearGradient id="progress-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={gradientColors[0]} />
            <stop offset="100%" stopColor={gradientColors[1]} />
          </linearGradient>
        </defs>
        {/* Outer white circle */}
        <circle
          cx="960"
          cy="432"
          r={radiusOuter}
          stroke="#FFF"
          strokeWidth="16"
          fill="none"
        />

        {/* Blue progress circle */}
        <circle
          cx="960"
          cy="432"
          r={radiusOuter}
          stroke="url(#progress-gradient)"
          strokeWidth="16"
          fill="none"
          strokeLinecap="square"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform="rotate(-90 960 432)"
        />
        
        {/* Hollow inner circle */}
        <circle
          cx="960"
          cy="432"
          r={radiusInner}
          fill="none"
        />
        
        
      </svg>
        {/* Percentage text */}
        <div
          style={{
          fontSize: "74px",
          fontFamily: 'abel',
          textAlign: 'center',
          position: 'absolute',
          width: '166px',
          top: '385px',
          left: '878px',
          zIndex: 20,
          color: '#00B0F0'
        }}
        >
          {`${Math.round(percentage)}%`}
        </div>
        <div
          style={{
          fontSize: "45px",
          fontFamily: 'abel',
          textAlign: 'center',
          position: 'absolute',
          width: '231px',
          top: '548px',
          left: '845px',
          zIndex: 20,
          color: 'white'
        }}
        >
          Analyzing
        </div>
    </div>
  );
};

export default CircularProgress;