const PhaseSquare = ({ 
  phaseNumber, 
  currentPhase, 
  backendStatus,
  imageData,  // Add this prop
  onRetake, 
  onResetPoints, 
  onConfirm,
  isLoading
}) => {
  // Determine which image to show
  const imageToShow = imageData[phaseNumber]?.imageUrl || require(`/${phaseNumber}.png`);
  
  return (
    <div className={`phaseSquare ${phaseNumber === currentPhase ? "active" : ''}`}>
      <div className={"imageContainer"}>
        <img 
          src={imageToShow}
          alt={`Phase ${phaseNumber}`} 
          className={"phaseImage"}
        />
        {phaseNumber === currentPhase && backendStatus.has_valid_image && (
          <div className={"buttonContainer"}>
            <button 
              className={"button"} 
              onClick={onRetake}
              disabled={isLoading}
            >
              {isLoading ? 'Retaking...' : 'Retake image'}
            </button>
            <button 
              className={"button"} 
              onClick={onResetPoints}
              disabled={isLoading}
            >
              Reset points
            </button>
            <button 
              className={"button"} 
              onClick={onConfirm}
              disabled={isLoading}
            >
              Confirm
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default PhaseSquare;