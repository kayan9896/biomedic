import React from 'react';

const PhaseSquare = ({ 
  phaseNumber, 
  currentPhase, 
  backendStatus, 
  onRetake, 
  onResetPoints, 
  onConfirm 
}) => {
  return (
    <div className={`phaseSquare ${phaseNumber === currentPhase ? 'active' : ''}`}>
      <div className={"imageContainer"}>
        <img 
          src={require(`/${phaseNumber}.png`)} 
          alt={`Phase ${phaseNumber}`} 
          className={"phaseImage"}
        />
        {phaseNumber === currentPhase && backendStatus.has_valid_image && (
          <div className={"buttonContainer"}>
            <button className={"button"} onClick={onRetake}>Retake image</button>
            <button className={"button"} onClick={onResetPoints}>Reset points</button>
            <button className={"button"} onClick={onConfirm}>Confirm</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default PhaseSquare;