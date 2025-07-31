import React, { useState, useEffect, useRef } from 'react';
import './App.css';
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
import leftCupTemplate from './L21/cuptemplate-l.json';
import rightCupTemplate from './L21/cuptemplate-r.json';
import leftTriTemplate from './L21/tritemplate-l.json';
import rightTriTemplate from './L21/tritemplate-r.json';
import ReconnectionPage from './L13/ReconnectionPage';
import L17 from './L17/L17';
import KB from './KB';

function App() {
  
  const [patient, setPatient] = useState('');
  const [ratio, setRatio] = useState('');
  const [comment, setComment] = useState('');

  const [showKeyboard, setShowKeyboard] = useState(false);
  const [keyboardLayout, setKeyboardLayout] = useState('default');

  const [isConnected, setIsConnected] = useState(false);
  const previousImgCountRef = useRef(0); 

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
  const pelvisRef = useRef([]); 

  const [leftImage, setLeftImage] = useState(getInstruction(stage,'AP'));
  const [rightImage, setRightImage] = useState(getInstruction(stage,'OB'));
  const [errImage, setErrImage] = useState(null);
  const [error, setError] = useState(null);

  const [leftImageMetadata, setLeftImageMetadata] = useState(null);
  const [rightImageMetadata, setRightImageMetadata] = useState(null);
  const [leftCheckMark, setLeftCheckMark] = useState(null);
  const [rightCheckMark, setRightCheckMark] = useState(null);
  const [useai, setUseai] = useState([false, false])
  const [recon, setRecon] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const useaiRef = useRef([]); 

  const [scn, setScn] = useState(0);
  const [tiltAngle, setAngle] = useState(0);
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

  const [applyTarget, setApplyTarget] = useState(false)
  const [targetTiltAngle, setTargetTiltAngle] = useState(null);
  const [apRotationAngle, setAPRotationAngle] = useState(null);
  const [obRotationAngle, setOBRotationAngle] = useState(null);
  const [obRotationAngle2, setOBRotationAngle2] = useState(null);
  const [isCupReg, setIsCupReg] = useState(null)
  const [isTriReg, setIsTriReg] = useState(null)
  const [usedOB, setUsedOB] = useState(null)

  const [selectCup, setSelectCup] = useState(true)

  const [resetWarning, setResetWarning] = useState(false);
  const [showReconnectionPage, setShowReconnectionPage] = useState(false);
  const handleReconnectionReturn = () => {
    setShowReconnectionPage(false);
  };

  function getInstruction (stage, side) {
    if (stage === 0 || stage === 1){
      return side === 'AP' ? require('./Instruction/RefAPInstruction.png') : require('./Instruction/RefOBInstruction.png')
    }
    if (stage === 2){
      return side === 'AP' ? require('./Instruction/CupAPInstruction.png') : require('./Instruction/CupOBInstruction.png')
    }
    if (stage === 3){
      return side === 'AP' ? require('./Instruction/TrialAPInstruction.png') : require('./Instruction/TrialOBInstruction.png')
    }
  }

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
  
  const getTemplate = (stage, pelvis, scaleFactor = 960 / 1024)=> {
    if (stage === 0 || stage === 1){
      return pelvis === 'l' ? scalePoints(leftTemplate, scaleFactor) : scalePoints(rightTemplate, scaleFactor);
    }
    if (stage === 2){
      return pelvis === 'l' ? scalePoints(leftCupTemplate, scaleFactor) : scalePoints(rightCupTemplate, scaleFactor);
    }
    if (stage === 3){
      return pelvis === 'l' ? scalePoints(leftTriTemplate, scaleFactor) : scalePoints(rightTriTemplate, scaleFactor);
    }
    return
  }

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
            setAngle(data.states.tilt_angle);
            setRotationAngle(data.states.rotation_angle);
            setImuon(data.states.imu_on);
            setVideo_on(data.states.video_on);
            setIsProcessing(data.states.is_processing);
            setProgress(data.states.progress);
            setStage(data.states.stage);
          }
          
          
          // Restore tilt_angle related states
          if (data.target_tilt_angle !== null) setTargetTiltAngle(data.states.target_tilt_angle);
          if (data.ap_rotation_angle !== null) setAPRotationAngle(data.states.ap_rotation_angle);
          if (data.ob_rotation_angle !== null) setOBRotationAngle(data.states.ob_rotation_angle);
          if (data.ob_rotation_angle2 !== null) setOBRotationAngle2(data.states.ob_rotation_angle2);
          
          const currentStageData = data.all_stage_data[data.states.stage]
          // IMPORTANT: Always reset both images to default first
          previousImgCountRef.current = data.states.img_count

          setLeftImage(getInstruction(stage,'AP'));
          setRightImage(getInstruction(stage,'OB'));
          setLeftImageMetadata(null);
          setRightImageMetadata(null);
          setLeftCheckMark(null);
          setRightCheckMark(null);
          
          
          if (currentStageData.ap_has_data && currentStageData.ap_image) {
            setLeftImage(currentStageData.ap_image);
            if (currentStageData.ap_metadata) {
              setLeftImageMetadata(currentStageData.ap_metadata);
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
            if (currentStageData.ob_metadata) {
              setRightImageMetadata(currentStageData.ob_metadata);
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

        setAngle(data.tilt_angle);
        setRotationAngle(data.rotation_angle);
        
        setIsProcessing(data.is_processing);
        setProgress(data.progress);
        setVideo_on(data.video_on)
        setImuon(data.imu_on)
        setAi_mode(data.ai_mode)
        setAutocollect(data.autocollect)
        setActiveLeft(data.active_side === 'ap' ? true: false)
        setActiveRight(data.active_side === 'ob' ? true: false)
        setApplyTarget(data.applytarget)
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
        setScn(data.scn)
        
        if (data.img_count !== previousImgCountRef.current) {
          previousImgCountRef.current = data.img_count;
          await updateImages(data.active_side, data.stage);
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

  
  const [testmeas, setTestmeas] = useState(null)
  const updateImages = async (active_side, stage) => {
    try {
        const response = await fetch('http://localhost:5000/api/image-with-metadata');
        const data = await response.json();

        if(data.jump){
          setStage(data.jump.stage)
          setLeftImage(data.jump.apimage === 'default' ? getInstruction(data.jump.stage, 'AP') : data.jump.apimage)
          setRightImage(data.jump.obimage === 'default' ? getInstruction(data.jump.stage, 'OB') : data.jump.obimage)
          setLeftImageMetadata(data.jump.apmetadata)
          setRightImageMetadata(data.jump.obmetadata)
          setLeftCheckMark(data.jump.checkmark)
          setRightCheckMark(data.jump.checkmark)
          setMeasurements(data.jump.measurements)
          setRecon(data.jump.recon)
          setMoveNext(data.jump.next)
          setPelvis([data.jump.side, data.jump.side])
          setUseai(data.jump.recon ? [true, true] : [false, false])
          setIsCupReg(data.jump.stage >= 2 && data.jump.next ? true : false)
          setIsTriReg(data.jump.stage === 3 && data.jump.next === 4 ? true : false)
          setTestmeas(data.jump.testmeas)
          setError(null)
          return
        }
        setTestmeas(null)
        setRecon(data.recon)
        setError(data.error)
        if(data.error==='glyph' || data.error === 'ref') {
          setShowglyph(data.error)
          setErrImage(data.image)
          return
        }

        if (active_side === 'ap') {
            setLeftImage(data.image);  // This is now a data URL
            setLeftImageMetadata(data.metadata);
            
            setLeftCheckMark(data.checkmark)
            setPelvis((prev) => {
              let tmp = [...prev]
              tmp[0] = data.side
              return tmp
            })
            console.log(stage, data.metadata)

            if(!data.recon) {
              setRightImage(getInstruction(stage,'OB'));
              setRightImageMetadata(null)
              setRightCheckMark(null)
              setUseai([data.metadata ? true : false, false])
            }
        } else if (active_side === 'ob') {
            setRightImage(data.image);  // This is now a data URL
            setRightImageMetadata(data.metadata);
            setRightCheckMark(data.checkmark)
            if(!data.recon) {
              setUseai(prev => {
                let tmp = [...prev]
                tmp[1] = data.metadata ? true : false
                return tmp
              })
            }
            setPelvis((prev) => {
              let tmp = [...prev]
              tmp[1] = data.side
              return tmp
            })
        }
        
        
        setMeasurements(data.measurements)

        if(stage === 2){
          if(data.measurements) setIsCupReg(true)
        }
        if(stage === 3){
          if(data.measurements) setIsTriReg(true)
        }
        
        setMoveNext(data.next)
        if(data.next) captureAndSaveFrame(stage)

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
    //captureAndSaveFrame()
  }
  const handlenext = async (next = 'next', keep = false) => {
    setPause(false)
    
    setLeftImageMetadata(null)
    setRightImageMetadata(null)
    leftSaveRefs.current = {}
    rightSaveRefs.current = {};
    setLeftCheckMark(null)
    setRightCheckMark(null)
    setRecon(null)
    setUseai([false, false])
    setPelvis([null, null])
    let st = next === 'next' ? stage + 1 : next === 'skip' ? stage + 2 : stage - 1;
    if(stage === 1 || stage === 2){
      setBrightness([100, 100])
      setContrast([100, 100])
    }
    if(!keep) {
      setLeftImage(getInstruction(st,'AP'));
      setRightImage(getInstruction(st,'OB'));
    }else{
      if(leftImage === getInstruction(stage,'AP')) setLeftImage(getInstruction(st,'AP'));
      if(rightImage === getInstruction(stage,'OB')) setRightImage(getInstruction(st,'OB'));
    }
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
    setEditing(leftImage!==getInstruction(stage,'AP') ? 'left' : 'right')
    useaiRef.current = useai
    pelvisRef.current = pelvis
    console.log(pelvisRef)
  };

  const handlerestart = async () => {
    setError(null)
    setLeftImage(getInstruction(0,'AP'));
    setRightImage(getInstruction(0,'OB'));
    setLeftImageMetadata(null)
    setRightImageMetadata(null)
    setLeftCheckMark(null)
    setRightCheckMark(null)
    setRecon(null)
    setIsCupReg(false)
    setIsTriReg(false)
    setStage(0);
    setUseai([false, false])
    setPelvis([null, null])
    setMeasurements(null)
    setTestmeas(null)
    setPause(0)
    setBrightness([100, 100])
    setContrast([100, 100])
    
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
          body: JSON.stringify({'uistates': editing || showCarm || isProcessing || pause || showglyph || report || showKeyboard ? 'edit' : null})
        });
        //setError(null)
      } catch (error) {
        console.error('Error setting edit UI state:', error);
        setError("Failed to set UIState");
      }
    };
  
    setEditUIState();
  }, [editing, showCarm, isProcessing, pause, showglyph, report, showKeyboard]);

  const leftSaveRefs = useRef({}); // Object to store refs by group for left side
  const rightSaveRefs = useRef({}); // Object to store refs by group for right side
  const clearFlagl = useRef(0)
  const clearFlagr = useRef(0)
  const setLeftTmp = (template) => { 
    if(!leftImageMetadata) {
      setLeftImageMetadata(template)
      clearFlagl.current = 1
    }
    else Object.values(leftSaveRefs.current).forEach(ref => ref?.setTmp?.(template));
  }
  const setRightTmp = (template) => {
    if(!rightImageMetadata) {
      setRightImageMetadata(template)
      clearFlagr.current = 1
    }
    else Object.values(rightSaveRefs.current).forEach(ref => ref?.setTmp?.(template));
  }
  const checkTmp = () => {
    const leftHasRed = Object.keys(leftSaveRefs.current).reduce((acc, group) => {
        const ref = leftSaveRefs.current[group];
        if (ref && typeof ref.checkTmp === 'function') {
          const groupMoved = ref.checkTmp();
          acc = acc || groupMoved; // Only include the group-specific data
        }
        return acc;
      }, false);
    const rightHasRed = Object.keys(rightSaveRefs.current).reduce((acc, group) => {
        const ref = rightSaveRefs.current[group];
        if (ref && typeof ref.checkTmp === 'function') {
          const groupMoved = ref.checkTmp();
          acc = acc || groupMoved; // Only include the group-specific data
        }
        return acc;
      }, false);
    return leftHasRed || rightHasRed
  }
  const rmRed = () => {
    Object.values(leftSaveRefs.current).forEach(ref => ref?.removeRed?.())
    Object.values(rightSaveRefs.current).forEach(ref => ref?.removeRed?.())
  }
  const handleSave = async () => {
    try {
      rmRed()
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
          limgside: pelvis[0],
          rimgside: pelvis[1]
        }),
      });

      // Update saved metadata for all groups
      Object.values(leftSaveRefs.current).forEach(ref => ref?.updateSavedMetadata?.());
      Object.values(rightSaveRefs.current).forEach(ref => ref?.updateSavedMetadata?.());
      if (leftImage!==getInstruction(stage,'AP')) setLeftCheckMark(1)
      if (rightImage!==getInstruction(stage,'OB')) setRightCheckMark(1)
      clearFlagl.current = 0
      clearFlagr.current = 0
      setError(null)
      setEditing(false);
    } catch (error) {
      console.error('Error saving landmarks:', error);
      setError("Failed to save landmarks");
    }
  };

  const handleExit = async () => {
    setUseai(useaiRef.current)
    setPelvis(pelvisRef.current)
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
      if(clearFlagl.current){
        setLeftImageMetadata(null)
      }
      if(clearFlagr.current){
        setRightImageMetadata(null)
      }
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

  const captureAndSaveFrame = async (stage) => {
    console.log(frameRef)
    if (!frameRef.current) return;
    
    try {
      // Use html2canvas to capture the frame with all overlays
      await new Promise(r => setTimeout(r, 2000));
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
          console.log(`stage${stage} with overlays saved successfully!`);
        } else {
          throw new Error('Failed to save image with overlays');
        }
      }, 'image/png');
    } catch (err) {
      console.error('Error capturing and saving frame:', err);
      alert('Error saving image with overlays: ' + err.message);
    }
  };

    const applyTemplate = (side, targetSetter) => {
      const templateData = getTemplate(stage, side)
      targetSetter(templateData);
    };

    
    const [resetTemplate, setResetTemplate] = useState(false)
  // Need to determine if we should show L21
  const shouldShowL21 = () => {
    if (!editing) return false;

    if (pelvis[0] !== null && leftImageMetadata == null) {
      if (leftImage!==getInstruction(stage,'AP')) {
        applyTemplate(pelvis[0], setLeftTmp);}
    }
    if (pelvis[1] !== null && rightImageMetadata == null) {
      if (rightImage!==getInstruction(stage,'OB')) {
        applyTemplate(pelvis[0], setRightTmp);}
    }
    // Only run this logic when we have one side with pelvis and one without
    if (pelvis[0] == null && pelvis[1] !== null) {
      // If left side is active and has no metadata, apply the template
      if (leftImage!==getInstruction(stage,'AP')) {
        applyTemplate(pelvis[1], setLeftTmp);
        setPelvis((prev) => {
          let tmp = [...prev]
          tmp[0] = pelvis[1]
          return tmp
        })
      }
    }
    if (pelvis[0] !== null && pelvis[1] == null) {  
      // If right side is active and has no metadata, apply the template
      if (rightImage!==getInstruction(stage,'OB')) {
        applyTemplate(pelvis[0], setRightTmp);
        setPelvis((prev) => {
          let tmp = [...prev]
          tmp[1] = pelvis[0]
          return tmp
        })
      }
    }
    
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
      <div style={{position:'absolute',zIndex:2000,top:'0px',color:'yellow'}}>{scn},{stage}</div>
      {!isConnected ? (
        <div>
          {/*L13 Setup, render when iscoonected false*/}
          <L13 setPause={setPause} selectedCArm={selectedCArm} setSelectedCArm={setSelectedCArm} handleConnect={handleConnect} setIsConnected={setIsConnected} tracking={tracking} setTracking={setTracking}/>
        </div>
      ) : (
        <>
        {/*L1 Background*/}
        <L1 tracking={tracking} handlLabelClick={handlLabelClick} editing={editing}/>
        
        {/*L2 Status bar*/}
        <L2 
          setShowKeyboard={setShowKeyboard} 
          pid={patient} 
          setting={setting}
          setSetting={setSetting} 
          setExit={setExit}
          stage={stage} 
          moveNext={moveNext} 
          handlerestart={handlerestart} 
          handlenext={handlenext} 
          isCupReg={isCupReg}
          isTriReg={isTriReg}
          showCarmBox={showCarm}
          autocollect={autocollect}
          editing={editing}
          recon={recon}
          handlepause={handlepause}
          setSelectCup={setSelectCup}
          isProcessing={isProcessing}
          pause={pause}
          showReconnectionPage={showReconnectionPage}
          leftImage={leftImage}
          leftImageMetadata={leftImageMetadata}
          leftSaveRefs={leftSaveRefs}
          rightImage={rightImage}
          rightImageMetadata={rightImageMetadata}
          rightSaveRefs={rightSaveRefs}
          measurements={measurements}
          testmeas={testmeas}
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
          getInstruction={getInstruction}
          stage={stage}
          recon={recon}
        />

      
      
      {/*L6 Edit blur, render when editing true*/}
      <L6 editableSide={editing} setEditing={setEditing} hasAp={leftImage!==getInstruction(stage,'AP')} hasOb={rightImage!==getInstruction(stage,'OB')}/>

      {/*L7 Imaging, render when backend progress=100*/}
      {!editing&&<L7 handledit={handledit} setReport={setReport} editable={!(leftImage===getInstruction(stage,'AP')&&rightImage===getInstruction(stage,'OB'))} leftCheckMark={leftCheckMark} rightCheckMark={rightCheckMark} recon={recon} setPause={setPause}/>}


      {/*L8 Edit bar, render when editing true*/}
      {editing && <L8
            editing={editing}
            onSave={handleSave}
            onExit={handleExit}
            onReset={handleReset}
            brightness={brightness[editing === 'left' ? 0 : 1]}
            contrast={contrast[editing === 'left' ? 0 : 1]}
            onBrightnessChange={handleBrightnessChange}
            onContrastChange={handleContrastChange}
            useai={useai}
            setResetTemplate={setResetTemplate}
            checkTmp={checkTmp}
            resetWarning={resetWarning}
            setResetWarning={setResetWarning}
          />}
      
        
      {/*L9 Message box, render based on backend measurements or error*/}
      {(!pause && !editing && !isProcessing) && <L9 error={error} measurements={measurements} handlepause={handlepause} moveNext={moveNext} stage={stage} isCupReg={isCupReg} isTriReg={isTriReg} setExit={setExit}/>}
   
      {/*L10 Carmbox, render if backend tilt_angle changes*/}
      {(tracking && showCarm && !pause && !isProcessing && !editing) && 
          <L10 
          tiltAngle={tiltAngle} 
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
          applyTarget={applyTarget}
        />
      
        }

      {/*L19 Reg error*/}
      {(error==='reg fails' && stage===1) && <L19 handlerestart={handlerestart}/>}

      {/*L20 Glyph error*/}
      {showglyph && <L20 image={errImage} showglyph={showglyph} setShowglyph={setShowglyph}/>}

      {/*L21 Template Selection, render when editing is true and pelvis is null*/}
      {(resetTemplate || shouldShowL21()) && (
        <L21 
          pelvis={pelvis}
          setPelvis={setPelvis}
          hasAp={leftImage!==getInstruction(stage,'AP')}
          hasOb={rightImage!==getInstruction(stage,'OB')}
          setLeftTmp={setLeftTmp}
          setRightTmp={setRightTmp}
          editing={editing}
          setEditing={setEditing}
          resetTemplate={resetTemplate}
          setResetTemplate={setResetTemplate}
          setUseai={setUseai}
          leftTemplateData={getTemplate(stage, 'l')}
          rightTemplateData={getTemplate(stage, 'r')}
          setResetWarning={setResetWarning}
        />
      )}

      {/*L1x IMU and video icons, render based on backend params */}
      {!report && !editing && <>
      {tracking && 
        <>
        {imuon? (
          <img 
            src={require('./L7/IMUConnectionIcon.png')} style={{position:'absolute', top:'863px', left:'1825px', zIndex:12}}
          />
        ):(<img 
          src={require('./L7/IMUConnErrorNotice.png')} style={{position:'absolute', top:'864px', left:'1772px', animation: 'slideIn 0.5s ease-in-out', zIndex:12}} onClick={()=>setShowReconnectionPage(!showReconnectionPage)}
        />)}
        </>
      }
      {video_on ? (<img 
        src={require('./L7/VideoConnectionIcon.png')} style={{position:'absolute', top:'765px', left:'1825px',zIndex:12}}
      />):(<img 
        src={require('./L7/VideoConnErrorNotice.png')} style={{position:'absolute', top:'765px', left:'1772px', animation: 'slideIn 0.5s ease-in-out', zIndex:12}} onClick={()=>setShowReconnectionPage(!showReconnectionPage)}
      />)}
      </>}
      

      {/*L11 Report, render when report button clicked*/}
      {report&&<L11 setReport={setReport} stage={stage} setError={setError}/>}
            
      {/*L12 Pause, render when next button clicked */}
      {<L12 key={Math.random()} pause={pause} setPause={setPause} handlenext={handlenext} selectCup={selectCup}/>}

      {/*L14 Setting, render when setting true*/}
      {setting&&<L14 setSetting={setSetting} ai_mode={ai_mode} autocollect={autocollect} />}

      

      {/*L1x Progree bar, render based on backend params*/}
      {isProcessing && <CircularProgress percentage={progress} />}

      {showReconnectionPage &&
            <ReconnectionPage 
            selectedCArm={selectedCArm}
            onClose={handleReconnectionReturn} 
            videoConnected={video_on} 
            imuConnected={imuon} 
            setShowReconnectionPage={setShowReconnectionPage}
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
      <img src={exit ? require('./L2/ExitIconOn.png') : require('./L2/ExitIcon.png')} style={{'position':'absolute', top:'1016px', left:'1853px'}} onClick={()=>{setExit(true)}}/>
    </div>
  );
}

export default App;