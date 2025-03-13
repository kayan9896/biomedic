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
    '#0155BB', // tail (start)
    '#3792FF', // head (end)
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
          cy="496"
          r={radiusOuter}
          stroke="#FFF"
          strokeWidth="16"
          fill="none"
        />

        {/* Blue progress circle */}
        <circle
          cx="960"
          cy="496"
          r={radiusOuter}
          stroke="url(#progress-gradient)"
          strokeWidth="16"
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform="rotate(-90 960 496)"
        />
        
        {/* Hollow inner circle */}
        <circle
          cx="960"
          cy="496"
          r={radiusInner}
          stroke="#000"
          strokeWidth="1"
          fill="none"
        />
        {/* Percentage text */}
        <text
          x="877"
          y="433"
          textAnchor="start"
          dominantBaseline="hanging"
          fill="#3792FF"
          fontSize="74px"
          fontFamily='abel'
        >
          {`${Math.round(percentage)}%`}
        </text>
        <text
          x="865"
          y="503"
          textAnchor="start"
          dominantBaseline="hanging"
          fill="white"
          fontSize="39.6px"
          fontFamily='abel'
        >
          Analyzing
        </text>
      </svg>
    </div>
  );
};

export default CircularProgress;