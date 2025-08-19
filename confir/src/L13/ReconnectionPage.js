import React, { useState, useEffect } from 'react';

function ReconnectionPage({ selectedCArm, onClose, videoConnected, imuConnected, setShowReconnectionPage, tracking }) {
  // Start with video step if disconnected, otherwise IMU step
  const [currentStep, setCurrentStep] = useState(videoConnected ? 3 : 2);
  const [videoStatus, setVideoStatus] = useState(videoConnected);
  const [imuStatus, setImuStatus] = useState(imuConnected);
  const [videoFrame, setVideoFrame] = useState(null);
  const [tiltSensorBatteryLow, setTiltSensorBatteryLow] = useState(false);
  const [error, setError] = useState(null);
  
  // Check video connection
  const checkVideoConnection = async () => {
    try {
      const response = await fetch('http://localhost:5000/check-video-connection');
      if (!response.ok) {
        throw new Error('Failed to check video connection');
      }
      const data = await response.json();
      setVideoStatus(data.connected);
      
      // If connected and frame is provided, store it
      if (data.connected && data.frame) {
        setVideoFrame(data.frame);
      }
    } catch (err) {
      setError('Error checking video connection: ' + err.message);
      console.error(err);
    }
  };

  // Check IMU/tilt sensor connection
  const checkTiltSensor = async () => {
    try {
      const response = await fetch('http://localhost:5000/check-tilt-sensor');
      if (!response.ok) {
        throw new Error('Failed to check tilt sensor');
      }
      const data = await response.json();
      setImuStatus(data.connected);
      setTiltSensorBatteryLow(data.battery_low);
    } catch (err) {
      setError('Error checking tilt sensor: ' + err.message);
      console.error(err);
    }
  };

  // Handle continue/return button
  const handleContinue = () => {
    if (currentStep === 2 && videoStatus) {
      if (!imuStatus && tracking) {
        setCurrentStep(3); // Move to IMU step if it's not connected
      } else {
        onClose(); // Both connected, close the page
      }
    } else if (currentStep === 3 && imuStatus) {
      onClose(); // IMU reconnected, close the page
    }
  };

  // Get status information for each check item
  const getCheckStatus = (step) => {
    let background = '';
    let textColor, icon, isComplete = false;
    if (step === 3 && !tracking){
        background = '';
        textColor = '#686868';
        icon = 'CrossGray.png';
      }
    else if (step === 1) { // C-ARM is always completed
      textColor = '#00B0F0';
      icon = 'CheckmarkBlue.png';
      isComplete = true;
    } else if (step === 2) { // Video connection
      if (step === currentStep) {
        // Current step
        background = 'StatusBg.png';
        textColor = '#FFFFFF';
        icon = videoStatus ? 'CheckmarkWhite.png' : 'CrossWhite.png';
        isComplete = videoStatus;
      } else {
        // Not current step
        textColor = videoStatus ? '#00B0F0' : '#FFFFFF';
        icon = videoStatus ? 'CheckmarkBlue.png' : 'CrossWhite.png';
        isComplete = videoStatus;
      }
    } else if (step === 3) { // IMU/Tilt sensor
      if (step === currentStep) {
        // Current step
        background = 'StatusBg.png';
        textColor = '#FFFFFF';
        icon = imuStatus ? 'CheckmarkWhite.png' : 'CrossWhite.png';
        isComplete = imuStatus;
      } else {
        // Not current step
        textColor = imuStatus ? '#00B0F0' : '#FFFFFF';
        icon = imuStatus ? 'CheckmarkBlue.png' : 'CrossWhite.png';
        isComplete = imuStatus;
      }
    } else if (step === 4) { // Reference bodies always completed
      textColor = '#00B0F0';
      icon = 'CheckmarkBlue.png';
      isComplete = true;
    }

    return { background, textColor, icon, isComplete };
  };

  // Render each check item
  const renderCheck = (step, title, yPos, yPos2, content) => {
    const status = getCheckStatus(step);
    return (
      <>
        {status.background && (
          <img src={require(`./${status.background}`)} style={{position:'absolute', zIndex:13, top:`${yPos}px`, left:'285px'}} />
        )}
        <img src={require(`./${status.icon}`)} style={{position:'absolute', zIndex:13, top:`${yPos+8}px`, left:'329px'}} />
        <div style={{position:'absolute', fontFamily:'abel', fontSize:'46px', color: status.textColor, width: '538px', zIndex:13, top:`${yPos+5}px`, left:'385px'}}>
          {title}
        </div>
        {content && (step === currentStep || step === 1 || step === 4 || 
                      (step === 2 && videoStatus) || 
                      (step === 3 && imuStatus)) && (
          <div style={{position:'absolute', fontFamily:'abel', fontSize:'30px', color: status.textColor, width: '498px', zIndex:13, top:`${yPos2}px`, left:'385px'}}>
            {content}
          </div>
        )}
      </>
    );
  };

  // Determine if current step is completed
  const isStepComplete = (step) => {
    switch (step) {
      case 2: return videoStatus;
      case 3: return imuStatus && !tiltSensorBatteryLow;
      default: return false;
    }
  };

  // Determine if all issues are resolved
  const allIssuesResolved = () => {
    return videoStatus && imuStatus && !tiltSensorBatteryLow;
  };

  // Determine if try again button should be enabled
  const isTryAgainEnabled = () => {
    return (currentStep === 2 && !videoStatus) || (currentStep === 3 && (!imuStatus || tiltSensorBatteryLow));
  };

  return (
    <div>
      <img src={require('../L10/BgBlur.png')} alt="ReportImageViewport" style={{position:'absolute', top:'0px', zIndex:13}}/>
      <img src={require('./SetupWindow.png')} alt="SetupWindow" style={{position:'absolute', top:'6px', left:'240px', zIndex:13}}/>
      
      {/* Try Again Button - always show but only enable for current active step that needs reconnection */}
      <img 
        src={isTryAgainEnabled() ? require('./SetupTryAgainBtn.png') : require('./SetupTryAgainBtnDisable.png')} 
        alt="SetupTryAgain" 
        style={{
          position:'absolute', 
          top:'839px', 
          left:'1002px', 
          zIndex:13, 
          cursor: isTryAgainEnabled() ? 'pointer' : 'default'
        }} 
        onClick={isTryAgainEnabled() ? (currentStep === 2 ? checkVideoConnection : checkTiltSensor) : null} 
      />
      
      {/* Continue/Return Button */}
      <img 
        src={allIssuesResolved() ? require('./ReturnBtn.png') : 
          (currentStep === 2 && !isStepComplete(3) ? (isStepComplete(2) ? require('./SetupContinueBtn.png') : require('./SetupContinueBtnDisable.png')) : 
          require('./SetupReturnBtnDisable.png'))
        }
        alt={allIssuesResolved() ? "Return" : "Continue"} 
        style={{
          position:'absolute', 
          top:'839px', 
          left:'1327px', 
          zIndex:13, 
          cursor: isStepComplete(currentStep) ? 'pointer' : 'default'
        }} 
        onClick={isStepComplete(currentStep) ? handleContinue : null} 
      />

      {/* Check 1: C-ARM EQUIPMENT - Always shown as completed */}
      {renderCheck(1, 'C-ARM EQUIPMENT', 144, 289, 'C-arm model is confirmed.')}
      
      {/* Disabled dropdown showing selected C-arm */}
      <select 
        disabled={true}
        style={{position:'absolute', paddingLeft:'10px', fontFamily:'abel', fontSize:'30px', zIndex:13, width: '546px', height:'58px', top:'224px', left:'329px', border: '1px solid #E5E5E5', borderRadius:'7.5px'}}>
        <option>{selectedCArm}</option>
      </select>
      
      {/* Check 2: VIDEO CONNECTION */}
      {renderCheck(2, 'VIDEO CONNECTION', 356, 435,
        videoStatus ? 'Video input detected successfully.' : 'Video input not detected.'
      )}
      
      {/* Check 3: TILT SENSOR */}
      {renderCheck(3, 'TILT SENSOR', 501, 578,
        imuStatus ? (tiltSensorBatteryLow ? 'Tilt Sensor connected but battery is low.' : 'Tilt Sensor connected successfully.') : 'Tilt Sensor not connected.'
      )}
      
      {/* Check 4: REFERENCE BODIES - Always shown as completed */}
      {renderCheck(4, 'REFERENCE BODIES', 647, 649, '')}
      
      {/* Instructions based on current step */}
      {currentStep === 2 && videoStatus && (
        <img src={require('./VideoConnectionSucceedInstruction.png')} 
             style={{position:'absolute', zIndex:13, top:'134px', left:'1015px'}} />
      )}
      
      {currentStep === 2 && !videoStatus && (
        <img src={require('./VideoConnectionFailedInstruction.png')} 
             style={{position:'absolute', zIndex:13, top:'134px', left:'1015px'}} />
      )}
      
      {currentStep === 3 && !imuStatus && (
        <img src={require('./TiltSensorFailedInstruction.png')} 
             style={{position:'absolute', zIndex:13, top:'134px', left:'1015px'}} />
      )}
      
      {currentStep === 3 && imuStatus && (
        <img src={tiltSensorBatteryLow ? require('./TiltSensorLowBatteryInstruction.png') : require('./TiltSensorSucceedInstruction.png')} 
             style={{position:'absolute', zIndex:13, top:'134px', left:'1015px'}} />
      )}
      
      
      {/* Video frame */}
      {currentStep === 2 && videoStatus && videoFrame && (
        <img 
          src={videoFrame}
          alt="Video feed"
          style={{
            position: 'absolute', 
            zIndex: 14, 
            top: '140px', 
            left: '1025px',
            maxWidth: '500px',
            maxHeight: '400px'
          }}
        />
      )}

      <img
        src={require('../ExitButton.png')}
        onClick={() => setShowReconnectionPage(false)} 
        style={{
          position: 'absolute',
          top: '59px',
          left: '1568px',
          zIndex: 13
        }}
      />
    </div>
  );
}

export default ReconnectionPage;