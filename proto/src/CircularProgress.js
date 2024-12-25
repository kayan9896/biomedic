import React from 'react';
import './CircularProgress.css';

const CircularProgress = ({ percentage }) => {
  const circumference = 2 * Math.PI * 45; // radius is 45
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <div className="circular-progress">
      <svg width="120" height="120" viewBox="0 0 120 120">
        {/* Grey background circle */}
        <circle
          cx="60"
          cy="60"
          r="45"
          stroke="#e6e6e6"
          strokeWidth="10"
          fill="none"
        />
        {/* Dark green inner circle */}
        <circle
          cx="60"
          cy="60"
          r="40"
          fill="#004d00"
        />
        {/* Blue progress circle */}
        <circle
          cx="60"
          cy="60"
          r="45"
          stroke="#007bff"
          strokeWidth="10"
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform="rotate(-90 60 60)"
        />
        {/* Percentage text */}
        <text
          x="60"
          y="60"
          textAnchor="middle"
          dominantBaseline="middle"
          fill="white"
          fontSize="24px"
        >
          {`${Math.round(percentage)}%`}
        </text>
      </svg>
    </div>
  );
};

export default CircularProgress;