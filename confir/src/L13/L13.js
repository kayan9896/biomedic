import React, { useState, useEffect } from 'react';

function L13({ setPause, selectedCArm, setSelectedCArm, handleConnect }) {
  const [cArms, setCArms] = useState({});
  const [cArmSelected, setCarmSelected] = useState(false);
  const [videoConnected, setVideoConnected] = useState(false);
  const [videoFrame, setVideoFrame] = useState(null);
  const [error, setError] = useState(null);
  const [tiltSensorConnected, setTiltSensorConnected] = useState(false);
  const [tiltSensorBatteryLow, setTiltSensorBatteryLow] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [allChecksComplete, setAllChecksComplete] = useState(false);
  const [warning, setWarning] = useState(false)
  const [carmimg, setCarmimg] = useState(false)
  
  // Fetch C-arm data when component mounts
  useEffect(() => {
    if(Object.keys(cArms).length > 0) return
    const fetchCArms = async () => {
      try {
        const response = await fetch('http://localhost:5000/get-carms');
        if (!response.ok) {
          throw new Error('Failed to fetch C-arm data');
        }
        const data = await response.json();
        setCArms(data);
        setError(null)
      } catch (err) {
        setError('Error loading C-arm data: ' + err.message);
        console.error(err);
      }
    };
    const intervalId = setInterval(fetchCArms, 100);
    
    return () => {
      clearInterval(intervalId);

    };
  });

  useEffect(() => {
    const fetchCArmimg = async () => {
      try {
        const response = await fetch(cArms[selectedCArm].image);
        if (!response.ok) {
          throw new Error('Failed to fetch C-arm img');
        }
        const data = await response.json();
        setCarmimg(data.image);
        setError(null)
      } catch (err) {
        setError('Error loading C-arm img: ' + err.message);
        console.error(err);
      }
    };
    fetchCArmimg()
  }, [selectedCArm]);

  const handleCarmChange = (e) => {
    setSelectedCArm(e.target.value);
    setCarmSelected(e.target.value !== '');
  };

  const checkVideoConnection = async () => {
    try {
      const response = await fetch('http://localhost:5000/check-video-connection');
      if (!response.ok) {
        throw new Error('Failed to check video connection');
      }
      const data = await response.json();
      setVideoConnected(data.connected);
      
      // If connected and frame is provided, store it
      if (data.connected && data.frame) {
        setVideoFrame(data.frame); // data.frame is a data URI (e.g., "data:image/jpeg;base64,...")
      }
    } catch (err) {
      setError('Error checking video connection: ' + err.message);
      console.error(err);
    }
  };

  // Simulate tilt sensor check
  const checkTiltSensor = async () => {
    try {
      const response = await fetch('http://localhost:5000/check-tilt-sensor');
      if (!response.ok) {
        throw new Error('Failed to check tilt sensor');
      }
      const data = await response.json();
      setTiltSensorConnected(data.connected);
      setTiltSensorBatteryLow(data.battery_low);
      
    } catch (err) {
      setError('Error checking tilt sensor: ' + err.message);
      console.error(err);
    }
  };

  // Function to handle continue/next button
  const handleContinue = () => {
    if (currentStep === 1 && cArmSelected) {
      setCurrentStep(2);
      checkVideoConnection(); // Automatically check video when advancing to step 2
    } else if (currentStep === 2 && videoConnected) {
      setCurrentStep(3);
      checkTiltSensor(); // Automatically check tilt sensor when advancing to step 3
    } else if (currentStep === 3 && tiltSensorConnected) {
      setCurrentStep(4);
      setAllChecksComplete(true); // Final step
    } else if (currentStep === 4 && allChecksComplete) {
      handleConnect()
      setPause(10); // When all checks complete, proceed to next screen
    }
  };

  // Determine if the current step is completed
  const isCurrentStepComplete = () => {
    switch (currentStep) {
      case 1: return cArmSelected;
      case 2: return videoConnected;
      case 3: return tiltSensorConnected && !tiltSensorBatteryLow; // Only complete if connected AND battery OK
      case 4: return true; // For the reference bodies step
      default: return false;
    }
  };

  const getSelectedCArmImage = () => {
    if (!selectedCArm || !cArms[selectedCArm] || !carmimg) return null;
    
    return (
      <img 
        src={carmimg}
        alt={`${selectedCArm} preview`} 
        style={{
          position: 'absolute', 
          zIndex: 14, 
          top: '140px', 
          left: '1025px',
          maxWidth: '500px',
          maxHeight: '400px'
        }}
      />
    );
  };

  const getCheckStatus = (step) => {
    let background = 'StatusBg.png';
    let textColor, icon, isComplete = false;

    if (step < currentStep) {
      // Completed step
      background = '';
      textColor = '#00B0F0';
      if ((step === 1 && cArmSelected) || 
          (step === 2 && videoConnected) || 
          (step === 3 && tiltSensorConnected)) {
        icon = 'CheckmarkBlue.png';
        isComplete = true;
      } else {
        icon = 'CrossWhite.png'; // Fallback to white cross if needed
      }
    } else if (step === currentStep) {
      // Current step
      textColor = '#FFFFFF';
      if ((step === 1 && cArmSelected) || 
          (step === 2 && videoConnected) || 
          (step === 3 && tiltSensorConnected) || step === 4) {
        icon = 'CheckmarkWhite.png';
        isComplete = true;
      } else {
        icon = 'CrossWhite.png';
      }
    } else {
      // Not reached yet
      background = '';
      textColor = '#686868';
      icon = 'CrossGray.png';
    }

    return { background, textColor, icon, isComplete };
  };

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
        {content && step <= currentStep && (
          <div style={{position:'absolute', fontFamily:'abel', fontSize:'30px', color: status.textColor, width: '498px', zIndex:13, top:`${yPos2}px`, left:'385px'}}>
            {content}
          </div>
        )}
      </>
    );
  };

  return (
    <div>
      <img src={require('./SetupWindow.png')} alt="SetupWindow" style={{position:'absolute', top:'6px', left:'240px', zIndex:13}}/>
      {(currentStep ===2 || currentStep ===3) && <img 
        src={(currentStep === 2 && !videoConnected) || (currentStep === 3 && (!tiltSensorConnected || tiltSensorBatteryLow)) ? require('./SetupTryAgainBtn.png') : require('./SetupTryAgainBtnDisable.png')} 
        alt="SetupTryAgain" 
        style={{
          position:'absolute', 
          top:'839px', 
          left:'1002px', 
          zIndex:13, 
          cursor: (currentStep === 2 && !videoConnected) || (currentStep === 3 && (!tiltSensorConnected || tiltSensorBatteryLow)) ? 'pointer' : 'default'
        }} 
        onClick={
          currentStep === 2 && !videoConnected 
            ? checkVideoConnection 
            : currentStep === 3 && (!tiltSensorConnected || tiltSensorBatteryLow) 
              ? checkTiltSensor 
              : null
        } 
      />}
      <img 
        src={isCurrentStepComplete() ? require('./SetupContinueBtn.png') : require('./SetupContinueBtnDisable.png')} 
        alt="SetupReturn" 
        style={{
          position:'absolute', 
          top:'839px', 
          left: (currentStep ===2 || currentStep ===3) ? '1327px' : '1164px', 
          zIndex:13, 
          cursor: isCurrentStepComplete() ? 'pointer' : 'default'
        }} 
        onClick={isCurrentStepComplete() ? handleContinue : null} 
      />
      
      {/* Check 1: C-ARM EQUIPMENT */}
      {renderCheck(1, 'C-ARM EQUIPMENT', 144, 289,
        cArmSelected ? 'C-arm model is confirmed.' : 'Please select the C-arm model.'
      )}
      
      {(
        <select 
          value={selectedCArm}
          onChange={handleCarmChange}
          disabled={currentStep>1}
          style={{position:'absolute', paddingLeft:'10px',fontFamily:'abel', fontSize:'30px', zIndex:13, width: '546px', height:'58px', top:'224px', left:'329px', border: '1px solid #E5E5E5', borderRadius:'7.5px'}}>
            <option value="" >Select a C-arm model</option>
            {Object.keys(cArms).map(carmName => (
              <option key={carmName} value={carmName}>{carmName}</option>
            ))}
        </select>
      )}
      
      {/* Check 2: VIDEO CONNECTION */}
      {renderCheck(2, 'VIDEO CONNECTION', 356, 435,
        videoConnected ? 'Video input detected successfully.' : 'Video input not detected.'
      )}
      
      {/* Check 3: TILT SENSOR */}
      {renderCheck(3, 'TILT SENSOR', 501, 578,
        tiltSensorConnected ? (tiltSensorBatteryLow ? 'Tilt Sensor connected but battery is low.' : 'Tilt Sensor connected successfully.') : 'Tilt Sensor not connected.'
      )}
      
      {/* Check 4: REFERENCE BODIES */}
      {renderCheck(4, 'REFERENCE BODIES', 647, 649, null)}
      
      {/* Instructions based on current step */}
      {currentStep === 1 && (
        <img src={require('./C-armEquipmentInstruction.png')} 
             style={{position:'absolute', zIndex:13, top:'134px', left:'1015px'}} />
      )}
      
      {currentStep === 2 && videoConnected && (
        <img src={require('./VideoConnectionSucceedInstruction.png')} 
             style={{position:'absolute', zIndex:13, top:'134px', left:'1015px'}} />
      )}
      
      {currentStep === 2 && !videoConnected && (
        <img src={require('./VideoConnectionFailedInstruction.png')} 
             style={{position:'absolute', zIndex:13, top:'134px', left:'1015px'}} />
      )}
      
      {currentStep === 3 && !tiltSensorConnected && (
        <img src={require('./TiltSensorFailedInstruction.png')} 
             style={{position:'absolute', zIndex:13, top:'134px', left:'1015px'}} />
      )}
      
      {currentStep === 3 && tiltSensorConnected && (
        <img src={tiltSensorBatteryLow ? require('./TiltSensorLowBatteryInstruction.png') : require('./TiltSensorSucceedInstruction.png')} 
             style={{position:'absolute', zIndex:13, top:'134px', left:'1015px'}} />
      )}
      
      {currentStep === 4 && (
        <img src={require('./ReferenceBodiesInstruction.png')} 
             style={{position:'absolute', zIndex:13, top:'134px', left:'1015px'}} />
      )}
      
      {/* Selected C-arm Image */}
      {currentStep === 1 && cArmSelected && getSelectedCArmImage()}
      
      {/* Video frame */}
      {currentStep === 2 && videoConnected && videoFrame && (
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

      <img className="image-button" src={require('./RestartBtn.png')} style={{position:'absolute', top:'839px', left:'284px', zIndex:13}} onClick={()=>setWarning(true)} />
      {warning&&<>
        <img src={require('../L10/BgBlur.png')} style={{position:'absolute', top:'0px', zIndex:15, aspectRatio:'1920/1080',height:'1080px'}}/>
        <img src={require('./RestartWarningWindow.png')} style={{position:'absolute', top:'358px', left:'612px', zIndex:15}} />
        <img className="image-button" src={require('../L23/YesBtn.png')} style={{position:'absolute', top:'539px', left:'761px', zIndex:15}} onClick={()=>{setCurrentStep(1); setWarning(false)}}/>
        <img className="image-button" src={require('../L23/NoBtn.png')} style={{position:'absolute', top:'539px', left:'1035px', zIndex:15}} onClick={()=>setWarning(false)}/>
      </>}
      <img src={require('../L1/Logo.png')} style={{position:'absolute', top:'1041px', left:'13px'}} />

    </div>
  );
}

export default L13;