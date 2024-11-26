import React, { useState } from 'react';
import './App.css';

const HipOperationProgress = () => {
  const [currentStep, setCurrentStep] = useState(0);
  
  const steps = [
    'Preparation',
    'Image Taking',
    'Adjustment',
    'Report',
    'Completion'
  ];

  const handleNextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  return (
    <div className="container">
      <div className="progress-container">
        {steps.map((step, index) => (
          <div 
            key={index} 
            className={`step ${index <= currentStep ? 'completed' : ''}`}
          >
            <div className="step-number">{index + 1}</div>
            <div className="step-text">{step}</div>
          </div>
        ))}
      </div>
      
      {/* For demonstration purposes - you can remove this button in production */}
      {currentStep < steps.length - 1 && (
        <button onClick={handleNextStep} className="next-button">
          Complete Current Step
        </button>
      )}
    </div>
  );
};

export default HipOperationProgress;