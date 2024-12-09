const PhaseSquare = ({ 
  phaseNumber, 
  currentPhase, 
  backendStatus,
  imageData,
  imageDimensions,
  currentPoints,
  onRetake, 
  onResetPoints, 
  onConfirm,
  isLoading
}) => {
  const imageToShow = imageData[phaseNumber]?.imageUrl || require(`/${phaseNumber}.png`);
  const pointsToShow = phaseNumber === currentPhase ? currentPoints[phaseNumber] : imageData[phaseNumber]?.points;
  
  return (
    <div className={`phaseSquare ${phaseNumber === currentPhase ? "active" : ''}`}>
      <div className={"imageContainer"}>
        <img 
          src={imageToShow}
          alt={`Phase ${phaseNumber}`} 
          className={"phaseImage"}
        />
        {pointsToShow && pointsToShow.map((point, index) => (
          <div
            key={index}
            className={"point"}
            style={{
              left: `${(point.x / imageDimensions.width) * 100}%`,
              top: `${(point.y / imageDimensions.height) * 100}%`
            }}
          />
        ))}
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