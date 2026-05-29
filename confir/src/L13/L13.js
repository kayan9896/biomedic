import React, { useState, useEffect } from 'react';
import CircularProgress2 from '../CircularProgress2';

function L13({data, setStage, setError, fetchCarm, checkVideo, setcurrentStep }) {

  const [warning, setWarning] = useState(false)
  

  const handleCarmChange = (e) => {
    fetchCarm(e.target.value, data.carm_model[e.target.value].image)
  };

  const checkVideoConnection = async () => {
    checkVideo()
  };


  // Function to handle continue/next button
  const handleContinue = () => {
    if (data.currentStep === 1 && data.selectedCArm) {
      setcurrentStep(2);
      checkVideoConnection(); // Automatically check video when advancing to step 2
    } else if (data.currentStep === 2 && data.is_connected) {
        setcurrentStep(4);
      
    } else if (data.currentStep === 3 && isCurrentStepComplete()) {
      setcurrentStep(4);
    } else if (data.currentStep === 4) {
      setStage(1)
    }
  };

  // Determine if the current step is completed
  const isCurrentStepComplete = () => {
    switch (data.currentStep) {
      case 1: return data.carm_img;
      case 2: return data.is_connected;
      case 3: return (null && !null); // Only complete if connected AND battery OK
      case 4: return true; // For the reference bodies step
      default: return false;
    }
  };

  const getSelectedCArmImage = () => {
    if (!data.selectedCArm || !data.carm_model[data.selectedCArm] || !data.carm_img) return null;
    
    return (
      <img 
        src={data.carm_img}
        alt={`${data.selectedCArm} preview`} 
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

    if (step < data.currentStep) {
      // Completed step
      background = '';
      textColor = '#00B0F0';
      if (step === 3){
        background = '';
        textColor = '#686868';
        icon = 'CrossGray.png';
      }
      else if ((step === 1 && data.selectedCArm) || 
          (step === 2 && data.is_connected) || 
          (step === 3 && null)) {
        icon = 'CheckmarkBlue.png';
        isComplete = true;
      } else {
        icon = 'CrossWhite.png'; // Fallback to white cross if needed
      }
    } else if (step === data.currentStep) {
      // Current step
      textColor = '#FFFFFF';
      if ((step === 1 && data.selectedCArm) || 
          (step === 2 && data.is_connected) || 
          (step === 3 && null) || step === 4) {
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
        {content && step <= data.currentStep && (
          <div style={{position:'absolute', fontFamily:'abel', fontSize:'30px', color: status.textColor, width: '498px', zIndex:13, top:`${yPos2}px`, left:'385px'}}>
            {content}
          </div>
        )}
      </>
    );
  };

  return (
    <div >
      <img src={require('./SetupWindow.png')} alt="SetupWindow" style={{position:'absolute', top:'6px', left:'240px', zIndex:13}}/>
      {(data.currentStep ===2 || data.currentStep ===3) && <img 
        className={(data.currentStep === 2 && !data.is_connected) || (data.currentStep === 3 && (!null || null)) ? "image-button" : null}
        src={(data.currentStep === 2 && !data.is_connected) || (data.currentStep === 3 && (!null || null)) ? require('./SetupTryAgainBtn.png') : require('./SetupTryAgainBtnDisable.png')} 
        alt="SetupTryAgain" 
        style={{
          position:'absolute', 
          top:'839px', 
          left:'1002px', 
          zIndex:13, 
          cursor: (data.currentStep === 2 && !data.is_connected) || (data.currentStep === 3 && (!null || null)) ? 'pointer' : 'default'
        }} 
        onClick={
          data.currentStep === 2 && !data.is_connected 
            ? checkVideoConnection 
            : null
        } 
      />}
      <img 
      data-testid='ctnbtn'
        className={isCurrentStepComplete() ? "image-button" : null}
        src={isCurrentStepComplete() ? require('./SetupContinueBtn.png') : require('./SetupContinueBtnDisable.png')} 
        alt="SetupReturn" 
        style={{
          position:'absolute', 
          top:'839px', 
          left: (data.currentStep ===2 || data.currentStep ===3) ? '1327px' : '1164px', 
          zIndex:13, 
          cursor: isCurrentStepComplete() ? 'pointer' : 'default'
        }} 
        onClick={isCurrentStepComplete() ? handleContinue : null} 
      />
      
      {/* Check 1: C-ARM EQUIPMENT */}
      {renderCheck(1, 'C-ARM EQUIPMENT', 144, 289,
        data.selectedCArm ? 'C-arm model is confirmed.' : 'Please select the C-arm model.'
      )}
      
      {(
        <select 
          value={data.selectedCArm}
          onChange={handleCarmChange}
          disabled={data.currentStep>1}
          style={{position:'absolute', paddingLeft:'10px',fontFamily:'abel', fontSize:'30px', zIndex:13, width: '546px', height:'58px', top:'224px', left:'329px', border: '1px solid #E5E5E5', borderRadius:'7.5px'}}>
            <option value={null} >Select a C-arm model</option>
            {Object.keys(data.carm_model).map(carmName => (
              <option key={carmName} value={carmName}>{carmName}</option>
            ))}
        </select>
      )}
      
      {/* Check 2: VIDEO CONNECTION */}
      {renderCheck(2, 'VIDEO CONNECTION', 356, 435,
        data.is_connected ? 'Video input detected successfully.' : 'Video input not detected.'
      )}
      
      {/* Check 3: TILT SENSOR */}
      {renderCheck(3, 'TILT SENSOR', 501, 578,
        null ? (null ? 'Tilt Sensor connected but battery is low.' : 'Tilt Sensor connected successfully.') : 'Tilt Sensor not connected.'
      )}
      
      {/* Check 4: REFERENCE BODIES */}
      {renderCheck(4, 'REFERENCE BODIES', 647, 649, null)}
      
      {/* Instructions based on current step */}
      {data.currentStep === 1 && (
        <img src={require('./C-armEquipmentInstruction.png')} 
             style={{position:'absolute', zIndex:13, top:'134px', left:'1015px'}} />
      )}
      
      {data.currentStep === 2 && data.is_connected && (
        <img src={require('./VideoConnectionSucceedInstruction.png')} 
             style={{position:'absolute', zIndex:13, top:'134px', left:'1015px'}} />
      )}
      
      {data.currentStep === 2 && !data.is_connected && (
        <img src={require('./VideoConnectionFailedInstruction.png')} 
             style={{position:'absolute', zIndex:13, top:'134px', left:'1015px'}} />
      )}
      
      {data.currentStep === 3 && !null && (
        <img src={require('./TiltSensorFailedInstruction.png')} 
             style={{position:'absolute', zIndex:13, top:'134px', left:'1015px'}} />
      )}
      
      {data.currentStep === 3 && null && (
        <img src={null ? require('./TiltSensorLowBatteryInstruction.png') : require('./TiltSensorSucceedInstruction.png')} 
             style={{position:'absolute', zIndex:13, top:'134px', left:'1015px'}} />
      )}
      
      {data.currentStep === 4 && (
        <img src={require('./ReferenceBodiesInstruction.png')} 
             style={{position:'absolute', zIndex:13, top:'134px', left:'1015px'}} />
      )}
      
      {/* Selected C-arm Image */}
      {data.currentStep === 1 && data.selectedCArm && getSelectedCArmImage()}
      
      {/* Video frame */}
      {data.currentStep === 2 && data.is_connected && data.first_frame && (
        <img 
          src={data.first_frame}
          alt="Video feed"
          style={{
            position: 'absolute', 
            zIndex: 14, 
            top: '140px', 
            left: '1025px',
            maxWidth: '500px',
            maxHeight: '400px',
            border:'2px solid grey'
          }}
        />
      )}

      <img className="image-button" src={require('./RestartBtn.png')} style={{position:'absolute', top:'839px', left:'284px', zIndex:13}} onClick={()=>setWarning(true)} />
      {warning&&<>
        <img src={require('../L10/BgBlur.png')} style={{position:'absolute', top:'0px', zIndex:15, aspectRatio:'1920/1080',height:'1080px'}}/>
        <img src={require('./RestartWarningWindow.png')} style={{position:'absolute', top:'358px', left:'612px', zIndex:15}} />
        <img className="image-button" src={require('../L23/YesBtn.png')} style={{position:'absolute', top:'539px', left:'761px', zIndex:15}} onClick={()=>{setcurrentStep(1); setWarning(false)}}/>
        <img className="image-button" src={require('../L23/NoBtn.png')} style={{position:'absolute', top:'539px', left:'1035px', zIndex:15}} onClick={()=>setWarning(false)}/>
      </>}
      <img src={require('../L1/Logo.png')} style={{position:'absolute', top:'1041px', left:'13px'}} />
      {data.loading && !data.is_connected && <CircularProgress2/>}
    </div>
  );
}

export default L13;