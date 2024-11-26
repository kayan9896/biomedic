import React, { useState } from 'react';
import './App.css';

const steps = [
  'Preparation',
  'Image Taking',
  'Adjustment',
  'Report',
  'Completion'
];

function HipOperationSoftware() {
  const [currentStep, setCurrentStep] = useState(0);

  const handleNextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  return (
    <div className="hip-operation-container">
      <div className="progress-bar">
        {steps.map((step, index) => (
          <div
            key={step}
            className={`step ${index <= currentStep ? 'completed' : ''}`}
          >
            <span className="step-text">{step}</span>
            {index < steps.length - 1 && <div className="chevron"></div>}
          </div>
        ))}
      </div>
      
      <div className="content-area">
        <h2>{steps[currentStep]}</h2>
        <p>Content for {steps[currentStep]} step goes here.</p>
        
        {currentStep < steps.length - 1 && (
          <button onClick={handleNextStep} className="next-button">
            Complete & Proceed to Next Step
          </button>
        )}
        
        {currentStep === steps.length - 1 && (
          <div className="completion-message">
            All steps completed!
          </div>
        )}
      </div>
    </div>
  );
}

export default HipOperationSoftware;