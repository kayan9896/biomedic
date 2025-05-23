import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import Keyboard from 'react-simple-keyboard';
import 'react-simple-keyboard/build/css/index.css';
import CircularProgress from './CircularProgress';
import L1 from './L1/L1';
import L2 from './L2/L2';
import L6 from './L6/L6';
import L7 from './L7/L7';
import L8 from './L8/L8';
import L10 from './L10/L10';
import L11 from './L11/L11';
import L13 from './L13/L13';
import L12 from './L12/L12';
import L14 from './L14/L14';
import L9 from './L9/L9';
import L3 from './L3';
import "@fontsource/abel"; // Defaults to weight 400
import "@fontsource/abel/400.css"; // Specify weight
import L20 from './L20/L20';
import L19 from './L19/L19';
import html2canvas from 'html2canvas';
import L21 from './L21/L21';

import leftTemplate from './L21/template-l.json';
import rightTemplate from './L21/template-r.json';
import ReconnectionPage from './L13/ReconnectionPage';
import L17 from './L17/L17';
import KB from './KB';
function scalePoints(templateData, scaleFactor) {
  const scaledData = JSON.parse(JSON.stringify(templateData)); // Create a deep copy of the data

  // Function to scale a single point
  const scalePoint = (point) => point.map(coord => coord * scaleFactor);
  console.log(Object.keys(scaledData))
  // Loop through the groups and scale points
  Object.keys(scaledData).forEach(groupKey => {
      scaledData[groupKey].forEach(item => {
          item.points = item.points.map(scalePoint); // Scale each point
      });
  });

  return scaledData;
}

const scaleFactor = 960 / 1024;
const leftTemplateData = scalePoints(leftTemplate, scaleFactor);
const rightTemplateData = scalePoints(rightTemplate, scaleFactor);
function App() {
  
  const [patient, setPatient] = useState('');
  const [ratio, setRatio] = useState('');
  const [comment, setComment] = useState('');

  const [showKeyboard, setShowKeyboard] = useState(false);
  const [keyboardLayout, setKeyboardLayout] = useState('default');

  const [isConnected, setIsConnected] = useState(false);
  const previousImgCountRef = useRef(0); 

  const [leftImage, setLeftImage] = useState(require('./AP.png'));
  const [rightImage, setRightImage] = useState(require('./OB.png'));
  const [error, setError] = useState(null);

  const [leftImageMetadata, setLeftImageMetadata] = useState(null);
  const [rightImageMetadata, setRightImageMetadata] = useState(null);
  const [leftCheckMark, setLeftCheckMark] = useState(null);
  const [rightCheckMark, setRightCheckMark] = useState(null);
  const [recon, setRecon] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);

  const [editing, setEditing] = useState(false)
  const [report, setReport] = useState(false)
  const [pause, setPause] = useState(0)
  const [setting, setSetting] = useState(false)
  const [exit, setExit] = useState(false)
  const [measurements, setMeasurements] = useState(null)
  const [stage, setStage] = useState(0)
  const [showglyph, setShowglyph] =useState(false)
  const [moveNext, setMoveNext] = useState(false)
  const [pelvis, setPelvis] = useState([null, null])
  const frameRef = useRef(null);

  const [angle, setAngle] = useState(0);
  const [rotationAngle, setRotationAngle] = useState(0);
  const [activeLeft, setActiveLeft] = useState(false);
  const [activeRight, setActiveRight] = useState(false)
  const [imuon, setImuon] = useState(false);
  const [video_on, setVideo_on] = useState(false);
  const [ai_mode, setAi_mode] = useState(0);
  const [autocollect, setAutocollect] = useState(true)
  const [tracking, setTracking] = useState(true)
  const [showCarm, setShowCarm] = useState(false);
  const [showIcon, setShowIcon] = useState(false)
  const [tiltValid, setTiltValid] = useState(false)
  const [rotValid, setRotValid] = useState(false)
  const [obl, setObl] = useState(null)
  const [obr, setObr] = useState(null)
  const [tiltl, setTiltl] = useState(null)
  const [tiltr, setTiltr] = useState(null)
  const [rangel, setRangel] = useState(null)
  const [ranger, setRanger] = useState(null)
  const [apl, setApl] = useState(null)
  const [apr, setApr] = useState(null)
  const [scale, setScale] = useState(1)

  const [targetTiltAngle, setTargetTiltAngle] = useState(null);
  const [apRotationAngle, setAPRotationAngle] = useState(null);
  const [obRotationAngle, setOBRotationAngle] = useState(null);
  const [obRotationAngle2, setOBRotationAngle2] = useState(null);
  const [isCupReg, setIsCupReg] = useState(null)
  const [isTriReg, setIsTriReg] = useState(null)
  const [usedOB, setUsedOB] = useState(null)

  const [showReconnectionPage, setShowReconnectionPage] = useState(false);
  const handleReconnectionReturn = () => {
    setShowReconnectionPage(false);
  };

  useEffect(() => {
    const checkBackendState = async () => {
      try {
        const response = await fetch('http://localhost:5000/check-running-state');
        const data = await response.json();
        
        if (data.running) {
          // Backend is already running, restore the state
          setIsConnected(true);
          
          // Restore basic states
          if (data.states) {
            setAngle(data.states.angle);
            setRotationAngle(data.states.rotation_angle);
            setImuon(data.states.imu_on);
            setVideo_on(data.states.video_on);
            setIsProcessing(data.states.is_processing);
            setProgress(data.states.progress);
            setStage(data.states.stage);
          }
          
          
          // Restore angle related states
          if (data.target_tilt_angle !== null) setTargetTiltAngle(data.states.target_tilt_angle);
          if (data.ap_rotation_angle !== null) setAPRotationAngle(data.states.ap_rotation_angle);
          if (data.ob_rotation_angle !== null) setOBRotationAngle(data.states.ob_rotation_angle);
          if (data.ob_rotation_angle2 !== null) setOBRotationAngle2(data.states.ob_rotation_angle2);
          
          const currentStageData = data.all_stage_data[data.states.stage]
          // IMPORTANT: Always reset both images to default first
          previousImgCountRef.current = data.states.img_count

          setLeftImage(require('./AP.png'));
          setRightImage(require('./OB.png'));
          setLeftImageMetadata(null);
          setRightImageMetadata(null);
          setLeftCheckMark(null);
          setRightCheckMark(null);
          
          
          if (currentStageData.ap_has_data && currentStageData.ap_image) {
            setLeftImage(currentStageData.ap_image);
            if (currentStageData.ap_metadata.metadata) {
              setLeftImageMetadata(currentStageData.ap_metadata.metadata);
            }
            setLeftCheckMark(currentStageData.ap_checkmark);
            
            // Update AP side of pelvis if we have side data
            if (currentStageData.ap_side) {
              setPelvis(prev => {
                const newPelvis = [...prev];
                newPelvis[0] = currentStageData.ap_side;
                return newPelvis;
              });
            }
            console.log('Restored AP image and metadata for current stage');
          }
          
          // Only update right (OB) image if the current stage has valid OB data
          if (currentStageData.ob_has_data && currentStageData.ob_image) {
            setRightImage(currentStageData.ob_image);
            if (currentStageData.ob_metadata.metadata) {
              setRightImageMetadata(currentStageData.ob_metadata.metadata);
            }
            setRightCheckMark(currentStageData.ob_checkmark);
            
            // Update OB side of pelvis if we have side data
            if (currentStageData.ob_side) {
              setPelvis(prev => {
                const newPelvis = [...prev];
                newPelvis[1] = currentStageData.ob_side;
                return newPelvis;
              });
            }
            console.log('Restored OB image and metadata for current stage');
          }
          setMoveNext(data.move_next);
        }
      } catch (error) {
        console.error('Error checking backend state:', error);
      }
    };
    
    checkBackendState();
  }, []);

  useEffect(() => {
    if(!isConnected) return;
    const fetchStates = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/states');
        const data = await response.json();

        setAngle(data.angle);
        setRotationAngle(data.rotation_angle);
        
        setIsProcessing(data.is_processing);
        setProgress(data.progress);
        setVideo_on(data.video_on)
        setImuon(data.imu_on)
        setAi_mode(data.ai_mode)
        setAutocollect(data.autocollect)
        setTracking(data.tracking)
        setActiveLeft(data.active_side === 'ap' ? true: false)
        setActiveRight(data.active_side === 'ob' ? true: false)
        setAPRotationAngle(data.aptarget)
        setOBRotationAngle(data.obtarget1)
        setOBRotationAngle2(data.obtarget2)
        setTargetTiltAngle(data.tilttarget)
        setUsedOB(data.used_ob)
        setShowCarm(data.show_window)
        setShowIcon(data.show_icon)
        setTiltValid(data.is_tilt_valid)
        setRotValid(data.is_rot_valid)
        setObl(data.ob_min)
        setObr(data.ob_max)
        setTiltl(data.tiltl)
        setTiltr(data.tiltr)
        setRangel(data.rangel)
        setRanger(data.ranger)
        setApl(data.apl)
        setApr(data.apr)
        setScale(data.scale)
        
        if (data.img_count !== previousImgCountRef.current) {
          previousImgCountRef.current = data.img_count;
          await updateImages(data.active_side);
        }

        if (data.measurements) {
          setMeasurements(data.measurements);
        }
      } catch (error) {
        console.error('Error fetching states:', error);
        setError("Error connecting to server");
      }
    };

    const intervalId = setInterval(fetchStates, 100);
    
    return () => {
      clearInterval(intervalId);

    };
  });

  

  const updateImages = async (active_side) => {
    try {
        const response = await fetch('http://localhost:5000/api/image-with-metadata');
        const data = await response.json();
        
        if (active_side === 'ap') {
            setLeftImage(data.image);  // This is now a data URL
            setLeftImageMetadata(data.metadata.metadata);
            setLeftCheckMark(data.checkmark)
            setPelvis((prev) => {
              let tmp = [...prev]
              tmp[0] = data.side
              return tmp
            })
            console.log(data.metadata)

            setRightImage(require('./OB.png'));
            setRightImageMetadata(null)
            setRightCheckMark(null)
        } else if (active_side === 'ob') {
            setRightImage(data.image);  // This is now a data URL
            setRightImageMetadata(data.metadata.metadata);
            setRightCheckMark(data.checkmark)
            setPelvis((prev) => {
              let tmp = [...prev]
              tmp[1] = data.side
              return tmp
            })

        }
        setRecon(data.recon)
        setError(data.error)
        
        setMeasurements(data.measurements)

        if(stage === 2){
          if(data.measurements) setIsCupReg(true)
        }
        if(stage === 3){
          if(data.measurements) setIsTriReg(true)
        }
        if(data.error==='glyph') {console.log(data.error,error); setShowglyph(true)}
        setMoveNext(data.next)

    } catch (error) {
        console.error('Error fetching image:', error);
        setError("Error updating images");
    }
  };
 

  const handleConnect = async () => {
    try {
      const response = await fetch('http://localhost:5000/run2', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) throw new Error('Connection failed');
      setIsConnected(true);
    } catch (err) {
      setError('Error connecting to device: ' + err.message);
    }
  };
  const handlepause = async (num) => {
    setPause(num)
    captureAndSaveFrame()
  }
  const handlenext = async (next = 'next') => {
    setPause(false)
    setLeftImage(require('./AP.png'));
    setRightImage(require('./OB.png'));
    setLeftImageMetadata(null)
    setRightImageMetadata(null)
    setLeftCheckMark(null)
    setRightCheckMark(null)
    let st = next === 'next' ? stage + 1 : next === 'skip' ? stage + 2 : stage - 1;

    if(next === 'next') setStage(p => p + 1);
    if(next === 'skip') setStage(p => p + 2);
    if(!next) setStage(p => p - 1);
    setMoveNext(false);
    setMeasurements(null)

    try {
      await fetch('http://localhost:5000/next', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          'uistates': next ? next : 'prev',
          'stage': st
        })
      });
    } catch (error) {
      console.error('Error going next:', error);
      setError("Failed to change backend uistate");
    }
  };

  const handlLabelClick = async (label) => {
    try {
      await fetch('http://localhost:5000/label', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({'label': label})
      });
    } catch (error) {
      setError("Failed to change active side");
    }
  };

  const handledit = async () => {
    setEditing('left')
    try {
      await fetch('http://localhost:5000/edit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({'uistates': 'edit'})
      });
    } catch (error) {
      console.error('Error going next:', error);
      setError("Failed to change backend uistate edit");
    }
  };

  const handlerestart = async () => {
    setError(null)
    setLeftImage(require('./AP.png'));
    setRightImage(require('./OB.png'));
    setLeftImageMetadata(null)
    setRightImageMetadata(null)
    setLeftCheckMark(null)
    setRightCheckMark(null)
    setRecon(null)
    setIsCupReg(false)
    setIsTriReg(false)
    setStage(0);
    try {
      await fetch('http://localhost:5000/restart', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
    } catch (error) {
      console.error('Error restart:', error);
      setError("Failed to change backend uistate restart");
    }
  };

  useEffect(() => {
    const setEditUIState = async () => {
      try {
        await fetch('http://localhost:5000/edit', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({'uistates': showCarm || isProcessing || pause ? 'edit' : null})
        });
      } catch (error) {
        console.error('Error setting edit UI state:', error);
        setError("Failed to set UIState");
      }
    };
  
    setEditUIState();
  }, [showCarm, isProcessing, pause]);

  const leftSaveRefs = useRef({}); // Object to store refs by group for left side
  const rightSaveRefs = useRef({}); // Object to store refs by group for right side

  const handleSave = async () => {
    try {
      // Aggregate metadata from all groups
      const leftData = Object.keys(leftSaveRefs.current).reduce((acc, group) => {
        const ref = leftSaveRefs.current[group];
        if (ref && typeof ref.getCurrentMetadata === 'function') {
          const metadata = ref.getCurrentMetadata();
          acc[group] = metadata[group]; // Only include the group-specific data
        }
        return acc;
      }, {});

      const rightData = Object.keys(rightSaveRefs.current).reduce((acc, group) => {
        const ref = rightSaveRefs.current[group];
        if (ref && typeof ref.getCurrentMetadata === 'function') {
          const metadata = ref.getCurrentMetadata();
          acc[group] = metadata[group]; // Only include the group-specific data
        }
        return acc;
      }, {});

      // Send to backend
      await fetch('http://localhost:5000/landmarks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          stage: stage,
          leftMetadata: leftData,
          rightMetadata: rightData,
        }),
      });

      // Update saved metadata for all groups
      Object.values(leftSaveRefs.current).forEach(ref => ref?.updateSavedMetadata?.());
      Object.values(rightSaveRefs.current).forEach(ref => ref?.updateSavedMetadata?.());
      setEditing(false);
    } catch (error) {
      console.error('Error saving landmarks:', error);
      setError("Failed to save landmarks");
    }
  };

  const handleExit = async () => {
    try {
      await fetch('http://localhost:5000/edit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({'uistates': null})
      });
      Object.values(leftSaveRefs.current).forEach(ref => ref?.resetToLastSaved?.());
      Object.values(rightSaveRefs.current).forEach(ref => ref?.resetToLastSaved?.());
      setEditing(false);
    } catch (error) {
      console.error('Error going next:', error);
      setError("Failed to change backend uistate edit");
    }
  };

  const handleReset = () => {
    Object.values(leftSaveRefs.current).forEach(ref => ref?.resetToOriginal?.());
    Object.values(rightSaveRefs.current).forEach(ref => ref?.resetToOriginal?.());
  };

  const handleDelete = (both) => {
    const p = editing === 'left'? pelvis[0] : pelvis[1]
    if (both){
      let template = p === 'r'? leftTemplateData: rightTemplateData;
      Object.values(leftSaveRefs.current).forEach(ref => ref?.clearAllPatterns?.(template));
      Object.values(rightSaveRefs.current).forEach(ref => ref?.clearAllPatterns?.(template));
      setPelvis(p === 'l'? ['r','r']: ['l','l'])
    }else{ 
      let template = p === 'l'? leftTemplateData: rightTemplateData;
      if (editing === 'left') Object.values(leftSaveRefs.current).forEach(ref => ref?.clearAllPatterns?.(template));
      if (editing === 'right') Object.values(rightSaveRefs.current).forEach(ref => ref?.clearAllPatterns?.(template));
    }
  };

  const captureAndSaveFrame = async () => {
    console.log(frameRef)
    if (!frameRef.current) return;
    
    try {
      // Use html2canvas to capture the frame with all overlays
      const canvas = await html2canvas(frameRef.current, {
        useCORS: true,
        allowTaint: true,
        backgroundColor: null,
      });
      
      // Convert canvas to blob
      canvas.toBlob(async (blob) => {
        // Create form data and append the image
        const formData = new FormData();
        formData.append('image', blob, `stage${stage}.png`);
        
        // Send to backend
        const response = await fetch(`http://localhost:5000/screenshot/${stage}`, {
          method: 'POST',
          body: formData,
        });
        
        if (response.ok) {
          alert(`stage${stage} with overlays saved successfully!`);
        } else {
          throw new Error('Failed to save image with overlays');
        }
      }, 'image/png');
    } catch (err) {
      console.error('Error capturing and saving frame:', err);
      alert('Error saving image with overlays: ' + err.message);
    }
  };
/*
  useEffect(() => {

    // Function to load the appropriate template based on pelvis side
    const applyTemplate = (side, targetSetter) => {
      const templateData = side === 'l' ? leftTemplateData : rightTemplateData;
      targetSetter(templateData);
    };

    // Only run this logic when we have one side with pelvis and one without
    if (pelvis[0] == null && pelvis[1] !== null) {
      // If left side is active and has no metadata, apply the template
      if (leftImage!==require('./AP.png')) {
        applyTemplate(pelvis[1], setLeftImageMetadata);
        setPelvis((prev) => {
          let tmp = [...prev]
          tmp[0] = pelvis[1]
          return tmp
        })
      }
    }
    if (pelvis[0] !== null && pelvis[1] == null) {  
      // If right side is active and has no metadata, apply the template
      if (rightImage!==require('./OB.png')) {
        applyTemplate(pelvis[0], setRightImageMetadata);
        setPelvis((prev) => {
          let tmp = [...prev]
          tmp[0] = pelvis[0]
          return tmp
        })
      }
    }
  }, [ pelvis, leftImage, rightImage]);
*/
  // Need to determine if we should show L21
  const shouldShowL21 = () => {
    if (!editing) return false;
    
    // If at least one side is active and has no template, show L21
    return (pelvis[0] === null) && 
           (pelvis[1] === null);
  };

  const [brightness, setBrightness] = useState([100, 100]);
  const [contrast, setContrast] = useState([100, 100]);

  const handleBrightnessChange = (value) => {
    setBrightness(prev => {
      const newBrightness = [...prev];
      newBrightness[editing === 'left' ? 0 : 1] = value;
      return newBrightness;
    });
  };

  const handleContrastChange = (value) => {
    setContrast(prev => {
      const newContrast = [...prev];
      newContrast[editing === 'left' ? 0 : 1] = value;
      return newContrast;
    });
  };
  const [selectedCArm, setSelectedCArm] = useState('');


  return (
    <div className="app">
      
      {!isConnected ? (
        <div>
          {/*L13 Setup, render when iscoonected false*/}
          <L13 setPause={setPause} selectedCArm={selectedCArm} setSelectedCArm={setSelectedCArm} handleConnect={handleConnect}/>
        </div>
      ) : (
        <>
        {/*L1 Background*/}
        <L1 tracking={tracking} handlLabelClick={handlLabelClick}/>
        
        {/*L2 Status bar*/}
        <L2 
          setShowKeyboard={setShowKeyboard} 
          pid={patient} setSetting={setSetting} 
          setExit={setExit}
          stage={stage} 
          setStage={setStage} 
          moveNext={moveNext} 
          handlerestart={handlerestart} 
          handlenext={handlenext} 
          isCupReg={isCupReg}
          isTriReg={isTriReg}
          showCarmBox={showCarm}
          autocollect={autocollect}
          editing={editing}
          recon={recon}
        />

        {/*L3 Images, containing L4 landmarks and L5 viewport inside*/}
        <L3
          leftImage={leftImage}
          activeLeft={activeLeft}
          leftImageMetadata={leftImageMetadata}
          rightImage={rightImage}
          activeRight={activeRight}
          rightImageMetadata={rightImageMetadata}
          onSaveLeft={leftSaveRefs}
          onSaveRight={rightSaveRefs}
          frameRef={frameRef}
          editing={editing}
          brightness={brightness}
          contrast={contrast}
        />

      
      
      {/*L6 Edit blur, render when editing true*/}
      <L6 editableSide={editing} setEditing={setEditing}/>

      {/*L7 Imaging, render when backend progress=100*/}
      {(!editing&&!(leftImage===require('./AP.png')&&rightImage===require('./OB.png')))&&<L7 handledit={handledit} setReport={setReport} leftCheckMark={leftCheckMark} rightCheckMark={rightCheckMark} recon={recon} setPause={setPause}/>}


      {/*L8 Edit bar, render when editing true*/}
      {editing && <L8
            editing={editing}
            onSave={handleSave}
            onExit={handleExit}
            onReset={handleReset}
            onDelete={handleDelete}
            brightness={brightness[editing === 'left' ? 0 : 1]}
            contrast={contrast[editing === 'left' ? 0 : 1]}
            onBrightnessChange={handleBrightnessChange}
            onContrastChange={handleContrastChange}
          />}
      
        
      {/*L9 Message box, render based on backend measurements or error*/}
      {(!pause && !editing && !isProcessing) && <L9 error={error} measurements={measurements} handlepause={handlepause} moveNext={moveNext} stage={stage} isCupReg={isCupReg} isTriReg={isTriReg} setExit={setExit}/>}
   
      {/*L10 Carmbox, render if backend angle changes*/}
      {(tracking && showCarm && !pause && !isProcessing) && 
          <L10 
          angle={angle} 
          rotationAngle={rotationAngle} 
          activeLeft={activeLeft}
          activeRight={activeRight}
          apRotationAngle={apRotationAngle}
          obRotationAngle={obRotationAngle}
          obRotationAngle2={obRotationAngle2}
          targetTiltAngle={targetTiltAngle}
          stage={stage}
          isCupReg={isCupReg}
          usedOB={usedOB}
          showIcon={showIcon}
          tiltValid={tiltValid}
          rotValid={rotValid}
          obl={obl}
          obr={obr}
          tiltl={tiltl}
          tiltr={tiltr}
          apl={apl}
          apr={apr}
          rangel={rangel}
          ranger={ranger}
          scale={scale}
        />
      
        }

      {/*L19 Reg error*/}
      {(error==='reg fails' && stage===1) && <L19 handlerestart={handlerestart}/>}

      {/*L20 Glyph error*/}
      {showglyph && <L20 image={activeLeft? leftImage : (activeRight? rightImage :null)} setShowglyph={setShowglyph}/>}

      {/*L21 Template Selection, render when editing is true and pelvis is null*/}
      {shouldShowL21() && (
        <L21 
          setPelvis={setPelvis}
          setLeftImageMetadata={setLeftImageMetadata}
          setRightImageMetadata={setRightImageMetadata}
          activeLeft={activeLeft}
          activeRight={activeRight}
        />
      )}

      {/*L1x IMU and video icons, render based on backend params */}
      {imuon ? (
        <img 
          src={require('./L7/IMUConnectionIcon.png')} 
          style={{
            position:'absolute', 
            top:'863px', 
            left:'1825px',
            zIndex:14
          }}
        />
      ):(<img 
        src={require('./L7/IMUConnErrorNotice.png')} 
        style={{
          position:'absolute', 
          top:'864px', 
          left:'1772px',
          animation: 'slideIn 0.5s ease-in-out',
          zIndex:14
        }}
        onClick={()=>setShowReconnectionPage(!showReconnectionPage)}
      />)}
      {video_on ? (<img 
        src={require('./L7/VideoConnectionIcon.png')} 
        style={{position:'absolute', top:'765px', left:'1825px',zIndex:14}}
      />):(<img 
        src={require('./L7/VideoConnErrorNotice.png')} 
        style={{
          position:'absolute', 
          top:'765px', 
          left:'1772px',
          animation: 'slideIn 0.5s ease-in-out',
          zIndex:14
        }}
        onClick={()=>setShowReconnectionPage(!showReconnectionPage)}
      />)}
      

      {/*L11 Report, render when report button clicked*/}
      {report&&<L11 setReport={setReport} stage={stage} setError={setError}/>}
            
      {/*L12 Pause, render when next button clicked */}
      {<L12 pause={pause} setPause={setPause} handlenext={handlenext}/>}

      {/*L14 Setting, render when setting true*/}
      {setting&&<L14 setSetting={setSetting} ai_mode={ai_mode} autocollect={autocollect} tracking={tracking}/>}

      

      {/*L1x Progree bar, render based on backend params*/}
      {isProcessing && <CircularProgress percentage={progress} />}

      {showReconnectionPage &&
            <ReconnectionPage 
            selectedCArm={selectedCArm}
            onClose={handleReconnectionReturn} 
            videoConnected={video_on} 
            imuConnected={imuon} 
          />}
      
      {/*L1x Keyboard, render when showKeyboard true*/}
      {showKeyboard && (
          <KB
          pid={patient}
          ratio={ratio}
          setRatio={setRatio}
          comment={comment}
          setComment={setComment}
          setPatient={setPatient}
          setShowKeyboard={setShowKeyboard}
          keyboardLayout={keyboardLayout}
          setKeyboardLayout={setKeyboardLayout}
        />
        )}
  
        </>
      )}
      {/*L17 Exit, render when exit true*/}
      {exit&&<L17 setExit={setExit} handlerestart={handlerestart}/>}
      <img src={require('./L2/ExitIcon.png')} style={{'position':'absolute', top:'1016px', left:'1853px'}} onClick={()=>{setExit(true)}}/>
    </div>
  );
}

export default App;