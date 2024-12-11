import React, { useState } from 'react';
import './App.css';
import Reference from './Reference';
import Cup from './Cup';
import TimeDisplay from './TimeDisplay';

const steps = [
  'Preparation',
  'Image Taking',
  'Adjustment',
  'Report',
  'Completion'
];

function HipOperationSoftware() {
  const [currentStep, setCurrentStep] = useState(0);
  const [allPhasesCompleted, setAllPhasesCompleted] = useState(false);

  const handleStepClick = (index) => {
    setCurrentStep(index);
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return <Reference onAllPhasesCompleted={setAllPhasesCompleted} />;
      case 2:
        return <Cup />;
      default:
        return <p>Content for {steps[currentStep]} step goes here.</p>;
    }
  };

  return (
    <div className="hip-operation-container">
      <div className="progress-bar">
        <div className="steps-container">
          {steps.map((step, index) => (
            <div
              key={step}
              className={`step ${index <= currentStep ? 'completed' : ''} 
              }`}
              onClick={() => handleStepClick(index)}
              style={{ cursor: 'pointer' }}
            >
              <span className="step-text">{step}</span>
              {index < steps.length - 1 && <div className="chevron"></div>}
            </div>
          ))}
        </div>
        <TimeDisplay />
      </div>
      
      <div className="content-area">
        <h2>{steps[currentStep]}</h2>
        {renderStepContent()}
        
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