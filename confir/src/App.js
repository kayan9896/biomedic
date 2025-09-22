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
import ReconnectionPage from './L13/ReconnectionPage';
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
import L17 from './L17/L17';
import KB from './KB';
import L18 from './L18/L18';
import L24 from './L24/L24';
import L26 from './L26/L26';
import CircularProgress2 from './CircularProgress2';

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
  const [oriLeft, setOriLeft] = useState(leftImage)
  const [oriRight, setOriRight] = useState(rightImage)
  const [errImage, setErrImage] = useState(null);
  const [error, setError] = useState(null);
  const generalError = useRef(null)
  const [bugs, setBugs] = useState([])
  const [fullBugs, setFullBugs] = useState(false)

  const [leftImageMetadata, setLeftImageMetadata] = useState(null);
  const [rightImageMetadata, setRightImageMetadata] = useState(null);
  const [leftCheckMark, setLeftCheckMark] = useState(null);
  const [rightCheckMark, setRightCheckMark] = useState(null);
  const [useai, setUseai] = useState([false, false])
  const [recon, setRecon] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const useaiRef = useRef([]); 

  const [carmModel, setCarmModel] = useState('')
  const [scn, setScn] = useState(0);
  const [tiltAngle, setAngle] = useState(360);
  const [rotationAngle, setRotationAngle] = useState(360);
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
  const [isRecon, setIsRecon] = useState(null)
  const [isPelReg, setIsPelReg] = useState(null)
  const [isCupReg, setIsCupReg] = useState(null)
  const [isTriReg, setIsTriReg] = useState(null)
  const [usedOB, setUsedOB] = useState(null)

  const [selectCup, setSelectCup] = useState(true)
  const [templates, setTemplates] = useState(null)

  const [resetWarning, setResetWarning] = useState(false);
  const [showReconnectionPage, setShowReconnectionPage] = useState(false);
  const handleReconnectionReturn = () => {
    setShowReconnectionPage(false);
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
  
  const getTemplate = (stage, pelvis, scaleFactor = 960 / 1024)=> {
    if (stage === 0 || stage === 1){
      return pelvis === 'l' ? JSON.parse(JSON.stringify(templates[6])) : JSON.parse(JSON.stringify(templates[1]));
    }
    if (stage === 2){
      return pelvis === 'l' ? JSON.parse(JSON.stringify(templates[2])) : JSON.parse(JSON.stringify(templates[3]));
    }
    if (stage === 3){
      return pelvis === 'l' ? JSON.parse(JSON.stringify(templates[4])) : JSON.parse(JSON.stringify(templates[5]));
    }
    return
  }

  const [takeAP, setTakeAP] = useState('Move the C-arm to the AP View')

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
        window.electronAPI?.logError(error);
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
        if(!response.ok) throw new Error('Error connecting to server')
        const data = await response.json();

        setCarmModel(data['C-arm Model'])
        if(data.show_window && data.imu_on){
          if(tiltAngle !== 360 && rotationAngle !== 360 && (data.tilt_angle !== tiltAngle || data.rotation_angle !== rotationAngle)){
            console.log(data.tilt_angle, tiltAngle, data.rotation_angle, rotationAngle)
            setShowCarm(true)
            setTakeAP(null)
          }
        }else setShowCarm(false)
        setAngle(data.tilt_angle);
        setRotationAngle(data.rotation_angle);
        setTracking(data.tracking)
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
        setBugs(data.bugs)
        if(data.unexpected_error){
          generalError.current = `Backend Loop Error.`
          setGe(true)
        }
        
        if (data.img_count !== previousImgCountRef.current) {
          previousImgCountRef.current = data.img_count;
          await updateImages(data.active_side, data.stage);
        }

        if (data.measurements) {
          setMeasurements(data.measurements);
        }
        if(generalError.current === "Error connecting to server") setGe(false)
      } catch (e) {
        console.error('Error fetching states:', e);
        window.electronAPI?.logError(e);
        if(generalError.current !== "Error connecting to server"){
          generalError.current = "Error connecting to server"
          setGe(true)
        }
      }
    };

    const intervalId = setInterval(fetchStates, 100);
    
    return () => {
      clearInterval(intervalId);

    };
  });

  const adjustImage = async(base64, brightness = 0, contrast = 0) => {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = img.width;
        canvas.height = img.height;

        // Draw original image
        ctx.drawImage(img, 0, 0);

        // Get image data
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;

        // Apply brightness
        let bright = brightness - 100
        for (let i = 0; i < data.length; i += 4) {
            data[i] = Math.min(255, Math.max(0, data[i] + (data[i] * (bright / 100)))); // Red
            data[i + 1] = Math.min(255, Math.max(0, data[i + 1] + (data[i + 1] * (bright / 100)))); // Green
            data[i + 2] = Math.min(255, Math.max(0, data[i + 2] + (data[i + 2] * (bright / 100)))); // Blue

        }

        // Apply contrast
        let con = contrast - 100
        const factor = (259 * (con + 255)) / (255 * (259 - con));
        for (let i = 0; i < data.length; i += 4) {
            data[i] = Math.min(255, Math.max(0, factor * (data[i] - 128) + 128));
            data[i + 1] = Math.min(255, Math.max(0, factor * (data[i + 1] - 128) + 128));
            data[i + 2] = Math.min(255, Math.max(0, factor * (data[i + 2] - 128) + 128));
        }

        // Put modified data back
        ctx.putImageData(imageData, 0, 0);

        // Return new base64 string
        resolve(canvas.toDataURL());

      };
      img.src = base64;
    })
  }

  useEffect(() => {
    const update = async() => {
      if (oriLeft === getInstruction(stage, 'AP')) {
        setLeftImage(oriLeft)
        return;
      }
      const img = await adjustImage(oriLeft, brightness[0], contrast[0])
      setLeftImage(img)
    }
    update()
  }, [oriLeft, brightness[0], contrast[0]])

    useEffect(() => {
    const update = async() => {
      if (oriRight === getInstruction(stage, 'OB')) {
        setRightImage(oriRight)
        return;
      }
      const img = await adjustImage(oriRight, brightness[1], contrast[1])
      setRightImage(img)
    }
    update()
  }, [oriRight, brightness[1], contrast[1]])
  
  const [testmeas, setTestmeas] = useState(null)
  const updateImages = async (active_side, stage) => {
    try {
        capturing.current = true
        const response = await fetch('http://localhost:5000/api/image-with-metadata');
        const data = await response.json();

        if(data.jump){
          setStage(data.jump.stage)
          setOriLeft(data.jump.apimage === 'default' ? getInstruction(data.jump.stage, 'AP') : data.jump.apimage)
          setOriRight(data.jump.obimage === 'default' ? getInstruction(data.jump.stage, 'OB') : data.jump.obimage)
          setLeftImageMetadata(data.jump.apmetadata)
          setRightImageMetadata(data.jump.obmetadata)
          setLeftCheckMark(data.jump.checkmark)
          setRightCheckMark(data.jump.checkmark)
          setMeasurements(data.jump.measurements)
          setRecon(data.jump.recon)
          setMoveNext(data.jump.next)
          setPelvis([data.jump.side, data.jump.side])
          setUseai(data.jump.recon ? [true, true] : [false, false])
          setIsRecon(data.jump.stage > 0 || (data.jump.stage === 0 && data.jump.next) ? true : false)
          setIsPelReg(data.jump.stage > 1 || (data.jump.stage === 1 && data.jump.next) ? true : false)
          setIsCupReg(data.jump.stage >= 2 && data.jump.next ? true : false)
          setIsTriReg(data.jump.stage === 3 && data.jump.next === 4 ? true : false)
          setTestmeas(data.jump.testmeas)
          setError(null)
          if (data.jump.brightness) setBrightness(data.jump.brightness)
          else setBrightness([100, 100])
          if (data.jump.contrast) setContrast(data.jump.contrast)
          else setContrast([100, 100])
          capturing.current = false
          return
        }
        setTestmeas(null)
        
        setError(data.error)
        if(data.error==='glyph' || data.error === 'ref') {
          setShowglyph(data.error)
          setErrImage(data.image)
          capturing.current = false
          return
        }

        setRecon(data.recon)

        if (active_side === 'ap') {
            setOriLeft(data.image)
            setLeftImageMetadata(data.metadata);
            
            setLeftCheckMark(data.checkmark)
            setPelvis((prev) => {
              let tmp = [...prev]
              tmp[0] = data.side
              return tmp
            })
            console.log(stage, data.metadata)

            if(!data.recon) {
              setOriRight(getInstruction(stage,'OB'));
              setRightImageMetadata(null)
              setRightCheckMark(null)
              setUseai([data.metadata ? true : false, false])
            }
        } else if (active_side === 'ob') {
            setOriRight(data.image)
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
        
        setMoveNext(data.next)
        if(data.next) await captureAndSaveFrame(stage)
        
        setMeasurements(data.measurements)
        if(stage === 0){
          if(data.recon === 2) setIsRecon(true)
        }
        if(stage === 1){
          if(data.next) setIsPelReg(true)
            console.log(isPelReg,data.next)
        }
        if(stage === 2){
          if(data.measurements) setIsCupReg(true)
        }
        if(stage === 3){
          if(data.measurements) setIsTriReg(true)
        }
         
        capturing.current = false
    } catch (error) {
        console.error('Error fetching image:', error);
        generalError.current = null
        setError('Backend API error')
        setGe(true)
        capturing.current = false
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
      const data = await response.json()
      setTemplates(data.templates)
      setIsConnected(true);
    } catch (err) {
      console.log('Error connecting to device: ' + err.message);
      generalError.current = null
      setError('Backend API error')
      setGe(true)
    }
  };
  const handlepause = async (num) => {
    setPause(num)
    //captureAndSaveFrame()
  }
  const handlenext = async (next = 'next', keep = false) => {
    setPause(false)
    if(!activeLeft) setTakeAP('Move the C-arm to the AP View')
    setLeftImageMetadata(null)
    setRightImageMetadata(null)
    leftSaveRefs.current = {}
    rightSaveRefs.current = {};
    setLeftCheckMark(null)
    setRightCheckMark(null)
    setRecon(null)
    setUseai([false, false])
    if(!isCupReg) setPelvis([null, null])
    let st = next === 'next' ? stage + 1 : next === 'skip' ? stage + 2 : stage - 1;
    if(stage === 1 || stage === 2){
      setBrightness([100, 100])
      setContrast([100, 100])
    }
    if(!keep) {
      setOriLeft(getInstruction(st,'AP'));
      setOriRight(getInstruction(st,'OB'));
    }else{
      if(leftImage === getInstruction(stage,'AP')) setOriLeft(getInstruction(st,'AP'));
      if(rightImage === getInstruction(stage,'OB')) setOriRight(getInstruction(st,'OB'));
    }
    if(next === 'next') setStage(p => p + 1);
    if(next === 'skip') setStage(p => p + 2);
    if(!next) setStage(p => p - 1);
    setMoveNext(false);
    setMeasurements(null)
    setError(null)
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
      generalError.current = null
      setError('Backend API error')
      setGe(true)
    }
  };

  const handlLabelClick = async (label) => {
    try {
      const response = await fetch('http://localhost:5000/label', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({'label': label})
      });
      if (!response.ok) throw new Error('Switch label failed');
    } catch (error) {
      console.log(error)
      generalError.current = null
      setError('Backend API error')
      setGe(true)
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
    setEditing(false)
    setOriLeft(getInstruction(0,'AP'));
    setOriRight(getInstruction(0,'OB'));
    setLeftImageMetadata(null)
    setRightImageMetadata(null)
    setLeftCheckMark(null)
    setRightCheckMark(null)
    setRecon(null)
    setIsRecon(false)
    setIsPelReg(false)
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
    setPatient('')
    setRatio('')
    setComment('')
    try {
      const response = await fetch('http://localhost:5000/restart', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      if (!response.ok) throw new Error('Restart failed');
    } catch (error) {
      console.error('Error restart:', error);
      generalError.current = null
      setError('Backend API error')
      setGe(true)
    }
  };

  useEffect(() => {
    const setEditUIState = async () => {
      try {
        const response = await fetch('http://localhost:5000/edit', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({'uistates': editing || showCarm || pause || showglyph || report || showKeyboard ? 'edit' : null})
        });
        if (!response.ok) throw new Error('Set uistate failed');
      } catch (error) {
        console.error('Error setting edit UI state:', error);
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
    else leftSaveRefs.current?.setTmp?.(template);
  }
  const setRightTmp = (template) => {
    if(!rightImageMetadata) {
      setRightImageMetadata(template)
      clearFlagr.current = 1
    }
    else rightSaveRefs.current?.setTmp?.(template);
  }
  const checkTmp = () => {
    const leftHasRed = leftSaveRefs.current?.checkTmp?.();

    const rightHasRed = rightSaveRefs.current?.checkTmp?.();

    return leftHasRed || rightHasRed
  }
  const rmRed = () => {
    leftSaveRefs.current?.removeRed?.()
    rightSaveRefs.current?.removeRed?.()
  }
  const handleSave = async () => {
    try {
      capturing.current = true
      rmRed()
      // Aggregate metadata from all groups
      const leftData = leftImageMetadata ? leftSaveRefs.current?.getCurrentMetadata() : null;

      const rightData = rightImageMetadata ? rightSaveRefs.current?.getCurrentMetadata() : null;

      // Send to backend
      const response = await fetch('http://localhost:5000/landmarks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          stage: stage,
          leftMetadata: leftData,
          rightMetadata: rightData,
          limgside: pelvis[0],
          rimgside: pelvis[1],
          brightness: brightness,
          contrast: contrast
        }),
      });
      if (!response.ok) throw new Error('Set landmarks failed');
      // Update saved metadata for all groups
      leftSaveRefs.current?.updateSavedMetadata?.();
      rightSaveRefs.current?.updateSavedMetadata?.();
      if (leftImage!==getInstruction(stage,'AP')) setLeftCheckMark(1)
      if (rightImage!==getInstruction(stage,'OB')) setRightCheckMark(1)
      clearFlagl.current = 0
      clearFlagr.current = 0
      setError(null)
      setEditing(false);
      //capturing.current = false
    } catch (error) {
      console.error('Error saving landmarks:', error);
      generalError.current = null
      setError('Backend API error')
      setGe(true)
      capturing.current = false
    }
  };

  const handleExit = async () => {
    setUseai(useaiRef.current)
    setPelvis(pelvisRef.current)
    try {
      
      leftSaveRefs.current?.resetToLastSaved?.();
      rightSaveRefs.current?.resetToLastSaved?.();
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
    if(editing === 'left') leftSaveRefs.current?.resetToOriginal?.();
    if(editing === 'right') rightSaveRefs.current?.resetToOriginal?.();
  };

  const capturing = useRef(false)
  const capturetxt = useRef(null)
  const captureAndSaveFrame = async (stage) => {
    console.log(frameRef)
    if (!frameRef.current) return;
    
    try {
      // Use html2canvas to capture the frame with all overlays
      capturing.current = true
      capturetxt.current = "Screenshot"
      //await new Promise(r => setTimeout(r, 2000));
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
        try{
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
        capturing.current = false
        capturetxt.current = ""
      } catch (err) {
        capturing.current = false
        capturetxt.current = ""
        generalError.current = null
        window.electronAPI?.logError('Backend API error');
        setError('Backend API error')
        setGe(true)
      }
      }, 'image/png');

    } catch (err) {
      capturing.current = false
      capturetxt.current = ""
      window.electronAPI?.logError(`Error capturing and saving frame: ${err}`);
      console.error('Error capturing and saving frame:', err);
      generalError.current = null
      setError('Backend API error')
      setGe(true)
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



  const handleDl = async () => {
      try{
        const res = await fetch(`http://localhost:5000/pdf`)
        const data = await res.json()
        if (!res.ok) {
          console.log(data.error)
          if (data.error == 'No path') setUsb(true)
          else {
            setError(data.error)
            setGe(true)
          }
        }
        else {
          setError('Saved!')
          setGe(true)
        }
      }catch(error){
        console.error('Error saving report:', error);
        alert(error)
      }
    }
  const [selectedCArm, setSelectedCArm] = useState('');
  const [usb, setUsb] = useState(false)
  const [ge, setGe] = useState(false)
  const [splash, setSplash] = useState(false)

  return (
    <div className="app">
      <div style={{position:'absolute',zIndex:2000,top:'0px',color:'yellow'}}>{scn},{stage}</div>
      <div style={{position:'absolute',zIndex:2000,top:'20px',color:'yellow'}} onClick={() => {setFullBugs(!fullBugs)}}>Exceptions:
        {fullBugs ? ((bugs.length > 0 ? (
          <div>
            {bugs.map((bug, i) => {
              return <div index={i}>{bug}</div>
            })}
          </div>) : 'None')
        ) : bugs.length}
      </div>
      {!isConnected ? (
        <div>
          {/*L13 Setup, render when iscoonected false*/}
          {splash ? <L24 setSplash={setSplash}/> : 
          <L13 setPause={setPause} selectedCArm={selectedCArm} setSelectedCArm={setSelectedCArm} handleConnect={handleConnect} setIsConnected={setIsConnected} tracking={tracking} setTracking={setTracking} setGe={setGe} setError={setError}/>
          }
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
          isRecon={isRecon}
          isPelReg={isPelReg}
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
          capturing={capturing}
        />

        {/*L3 Images, containing L4 landmarks and L5 viewport inside*/}
        <L3
          leftImage={leftImage}
          activeLeft={activeLeft}
          leftImageMetadata={leftImageMetadata}
          rightImage={rightImage}
          activeRight={activeRight}
          rightImageMetadata={rightImageMetadata}
          onSaveLeft={(ref) => {leftSaveRefs.current = ref}}
          onSaveRight={(ref) => {rightSaveRefs.current = ref}}
          frameRef={frameRef}
          editing={editing}
          brightness={brightness}
          contrast={contrast}
          getInstruction={getInstruction}
          stage={stage}
          recon={recon}
          tiltValid={tiltValid}
          rotValid={rotValid}
          tracking={tracking}
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
            setLeftTmp={setLeftTmp}
            setRightTmp={setRightTmp}
            stage={stage}
            pelvis={pelvis}
            getTemplate={getTemplate}
            isCupReg={isCupReg}
          />}
      
        
      {/*L9 Message box, render based on backend measurements or error*/}
      {(!pause && !editing && !isProcessing) && <L9 error={error} measurements={measurements} handlepause={handlepause} moveNext={moveNext} stage={stage} isCupReg={isCupReg} isTriReg={isTriReg} setExit={setExit} takeAP={takeAP}/>}
   
      {/*L10 Carmbox, render if backend tilt_angle changes*/}
      {(tracking && showCarm && !pause && !isProcessing && !editing && imuon) && 
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
          isTriReg={isTriReg}
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
          noap={leftImage===getInstruction(stage,'AP')}
        />
      
        }

      {/*L19 Reg error*/}
      {(error==='130') && <L19 handlerestart={handlerestart}/>}

      {/*L20 Glyph error*/}
      {showglyph && <L20 image={errImage} showglyph={showglyph} setShowglyph={setShowglyph}/>}

      {/*L21 Template Selection, render when editing is true and pelvis is null*/}
      {editing && (resetTemplate || shouldShowL21()) && (
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
      {report&&<L11 setReport={setReport} stage={stage} setError={setError} handleDl={handleDl}/>}
            
      {/*L12 Pause, render when next button clicked */}
      {<L12 pause={pause} setPause={setPause} handlenext={handlenext} selectCup={selectCup}/>}

      {/*L14 Setting, render when setting true*/}
      {setting&&<L14 setSetting={setSetting} ai_mode={ai_mode} autocollect={autocollect} />}

      

      {/*L1x Progree bar, render based on backend params*/}
      {isProcessing && <CircularProgress percentage={progress} />}
      {capturing.current && capturetxt.current && <CircularProgress2 txt={capturetxt.current}/>}

      {showReconnectionPage &&
            <ReconnectionPage 
            selectedCArm={carmModel}
            onClose={handleReconnectionReturn} 
            videoConnected={video_on} 
            imuConnected={imuon} 
            setShowReconnectionPage={setShowReconnectionPage}
            tracking={tracking}
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
      {exit&&<L17 setExit={setExit} handlerestart={handlerestart} handleDl={handleDl} capturing={capturing}/>}

      {usb && <L18 handleDl={handleDl} setUsb={setUsb}/>}

      {ge && <L26 txt={generalError.current ? generalError.current : error} setGe={setGe}/>};

      {!splash && <img src={exit ? require('./L2/ExitIconOn.png') : require('./L2/ExitIcon.png')} style={{'position':'absolute', top:'1016px', left:'1853px'}} onClick={()=>{setExit(true)}}/>}
    </div>
  );
}

export default App;