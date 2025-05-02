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
  const [angle, setAngle] = useState(0);
  const [patient, setPatient] = useState('');
  const [ratio, setRatio] = useState('');
  const [comment, setComment] = useState('');
  const [leftImage, setLeftImage] = useState(require('./AP.png'));
  const [rightImage, setRightImage] = useState(require('./OB.png'));
  const [error, setError] = useState(null);
  const [showKeyboard, setShowKeyboard] = useState(false);
  const keyboardRef = useRef(null);
  const [cursorPosition, setCursorPosition] = useState(0);
  const [keyboardLayout, setKeyboardLayout] = useState('default');

  const [showCarmBox, setShowCarmBox] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const previousImgCountRef = useRef(0); 
  const carmBoxTimerRef = useRef(null);
  const [rotationAngle, setRotationAngle] = useState(0);
  const previousRotationAngleRef = useRef(rotationAngle);
  const isInGreenSector = rotationAngle >= -20 && rotationAngle <= 20;
  const isInYellowSector = rotationAngle >= -50 && rotationAngle <= 50;
  const activeLeft = isInGreenSector;
  const activeRight = isInYellowSector && !isInGreenSector;
  const [imuon, setImuon] = useState(false);
  const [video_on, setVideo_on] = useState(false);
  const [ai_mode, setAi_mode] = useState(0);
  const [leftImageMetadata, setLeftImageMetadata] = useState(null);
  const [rightImageMetadata, setRightImageMetadata] = useState(null);
  const [leftCheckMark, setLeftCheckMark] = useState(null);
  const [rightCheckMark, setRightCheckMark] = useState(null);
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

  // New state variables for the angle tracking feature
  const [targetTiltAngle, setTargetTiltAngle] = useState(null);
  
  // New separate rotation angle states for AP and OB modes
  const [apRotationAngle, setAPRotationAngle] = useState(null);
  const [obRotationAngle, setOBRotationAngle] = useState(null);
  const [obRotationAngle2, setOBRotationAngle2] = useState(null);
  const [isCupReg, setIsCupReg] = useState(null)
  const [usedOB, setUsedOB] = useState(-12.3)

  const [tiltTaken, setTiltTaken] = useState(null)
  const [apTaken, setApTaken] = useState(null)
  const [obTaken, setObTaken] = useState(null)
  const [obTaken2, setObTaken2] = useState(null)
  
  const [isTiltSaved, setIsTiltSaved] = useState(false);
  
  // Separate saved states for AP and OB rotation
  const [isAPRotationSaved, setIsAPRotationSaved] = useState(false);
  const [isOBRotationSaved, setIsOBRotationSaved] = useState(false);
  
  // Get the currently active rotation saved state based on mode
  const isRotationSaved = activeLeft ? isAPRotationSaved : isOBRotationSaved;
  
  // References for the timers
  const tiltSaveTimerRef = useRef(null);
  const rotationSaveTimerRef = useRef(null);
  const windowCloseTimerRef = useRef(null);
  
  // References to track the last angle values
  const lastTiltAngleRef = useRef(angle);
  const lastRotationAngleRef = useRef(rotationAngle);
  const stageRef = useRef(stage);

  // Flag to track if this is the first load of the component
  const isFirstLoad = useRef(true);
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
    stageRef.current = stage;
    const fetchStates = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/states');
        const data = await response.json();
        
        // Get the current angles from the server
        const currentTiltAngle = data.angle;
        const currentRotationAngle = data.rotation_angle;
        
        // Check if this is the first load
        if (isFirstLoad.current) {
          isFirstLoad.current = false;
          
          // Set initial values
          setAngle(currentTiltAngle);
          setRotationAngle(currentRotationAngle);
          lastTiltAngleRef.current = currentTiltAngle;
          lastRotationAngleRef.current = currentRotationAngle;
          
          // If initial tilt angle is valid, mark it as saved
          if (currentTiltAngle >= -20 && currentTiltAngle <= 20) {
            setIsTiltSaved(true);
            setTargetTiltAngle(currentTiltAngle)
          }
          
          // If initial rotation angle is valid for its mode, mark it as saved
          const isInInitialAPMode = currentRotationAngle >= -20 && currentRotationAngle <= 20;
          
          if (isInInitialAPMode) {
            if (currentRotationAngle >= -20 && currentRotationAngle <= 20) {
              if(stageRef.current === 0){
              setIsAPRotationSaved(true);
              setAPRotationAngle(currentRotationAngle);
              console.log(1)
            }else{
              if (currentRotationAngle === apRotationAngle) setIsAPRotationSaved(true)
            }
            }
          } else if (currentRotationAngle >= -50 && currentRotationAngle <= 50) {
            const isInitialOBRotationValid = 
              (currentRotationAngle >= -50 && currentRotationAngle <= -20) || 
              (currentRotationAngle >= 20 && currentRotationAngle <= 50);
            
            if (isInitialOBRotationValid) {
              setIsOBRotationSaved(true);
              if(stage === 0){
              setOBRotationAngle(currentRotationAngle);}
              if(stage === 1){
                setOBRotationAngle2(currentRotationAngle)
              }
            }
          }
          
          return; // Skip the rest of the processing for the initial load
        }
        
        // Track if any angle changed
        let angleChanged = false;
        
        // Check if tilt angle has changed
        if (currentTiltAngle !== lastTiltAngleRef.current) {
          lastTiltAngleRef.current = currentTiltAngle;
          setAngle(currentTiltAngle);
          setIsTiltSaved(false);
          angleChanged = true;
          
          // Clear any existing tilt timer
          if (tiltSaveTimerRef.current) {
            clearTimeout(tiltSaveTimerRef.current);
          }
          
          // Set a new timer to mark tilt as saved after 3 seconds of no changes
          tiltSaveTimerRef.current = setTimeout(() => {
            const isTiltValid = currentTiltAngle >= -20 && currentTiltAngle <= 20;
            if (isTiltValid) {
              setIsTiltSaved(true);
            } else {
              // Force the carmbox to stay open by ensuring it's not saved
              setIsTiltSaved(false);
              
              // Re-check after a second (keep checking until angle is valid)
              setTimeout(() => {
                // Re-check current tilt value
                const currentIsTiltValid = angle >= -20 && angle <= 20;
                if (!currentIsTiltValid) {
                  // Force window to stay visible if tilt remains invalid
                  setShowCarmBox(true);
                }
              }, 1000);
            }
          }, 3000);
        } else if (!isTiltSaved && currentTiltAngle >= -20 && currentTiltAngle <= 20) {
          // If tilt hasn't changed but is valid and not saved, start a timer to save it
          if (!tiltSaveTimerRef.current) {
            tiltSaveTimerRef.current = setTimeout(() => {
              setIsTiltSaved(true);
            }, 3000);
          }
        }
        
        // Check if rotation angle has changed
        if (currentRotationAngle !== lastRotationAngleRef.current) {
          lastRotationAngleRef.current = currentRotationAngle;
          setRotationAngle(currentRotationAngle);
          angleChanged = true;
          
          // Reset the appropriate saved state based on current sector
          const isInAPMode = currentRotationAngle >= -20 && currentRotationAngle <= 20;
          
          if (isInAPMode) {
            // In AP mode
            setIsAPRotationSaved(false);
          } else if (currentRotationAngle >= -50 && currentRotationAngle <= 50) {
            // In OB mode
            setIsOBRotationSaved(false);
          }
          
          // Clear any existing rotation timer
          if (rotationSaveTimerRef.current) {
            clearTimeout(rotationSaveTimerRef.current);
          }
          
          // Set a new timer to mark rotation as saved after 3 seconds of no changes
          rotationSaveTimerRef.current = setTimeout(() => {
            // Check if we're in AP mode (rotation angle between -20 and 20 degrees)
            const isInCurrentAPMode = currentRotationAngle >= -20 && currentRotationAngle <= 20;
            
            if (isInCurrentAPMode) {
              // AP mode: rotation angle must be between -20 and 20
              const isAPRotationValid = currentRotationAngle >= -20 && currentRotationAngle <= 20;
              
              if (isAPRotationValid) {
                if(stageRef.current === 0){
                setIsAPRotationSaved(true);
                setAPRotationAngle(currentRotationAngle);
                console.log(stage, 2)
              }else{
                if (currentRotationAngle === apRotationAngle) setIsAPRotationSaved(true)
              }
              } else {
                setIsAPRotationSaved(false);
                
                // Re-check after a second
                setTimeout(() => {
                  const currentIsInAPMode = rotationAngle >= -20 && rotationAngle <= 20;
                  const currentIsAPRotationValid = rotationAngle >= -20 && rotationAngle <= 20;
                  
                  if (currentIsInAPMode && !currentIsAPRotationValid) {
                    // Force window to stay visible if angle remains invalid
                    setShowCarmBox(true);
                  }
                }, 1000);
              }
            } else if (currentRotationAngle >= -50 && currentRotationAngle <= 50) {
              // OB mode: rotation angle must be between -50 and -20 OR between 20 and 50
              const isOBRotationValid = stageRef.current === 0 ? (
                (currentRotationAngle >= -50 && currentRotationAngle <= -20) || 
                (currentRotationAngle >= 20 && currentRotationAngle <= 50)):
                (stageRef.current === 1 ?
                  (((currentRotationAngle >= -50 && currentRotationAngle <= -20) || 
                  (currentRotationAngle >= 20 && currentRotationAngle <= 50)) 
                  && currentRotationAngle * obRotationAngle < 0):
                  (currentRotationAngle === obRotationAngle || currentRotationAngle === obRotationAngle2)
                )
                  
              if (isOBRotationValid) {
                setIsOBRotationSaved(true);
                if(stageRef.current === 0){
                  setOBRotationAngle(currentRotationAngle);
                }
                if(stageRef.current === 1){
                  setOBRotationAngle2(currentRotationAngle);
                }
              } else {
                setIsOBRotationSaved(false);
                
                // Re-check after a second
                setTimeout(() => {
                  const currentIsInOBMode = 
                    rotationAngle >= -50 && rotationAngle <= 50 && 
                    !(rotationAngle >= -20 && rotationAngle <= 20);
                    
                  const currentIsOBRotationValid = 
                    (rotationAngle >= -50 && rotationAngle <= -20) || 
                    (rotationAngle >= 20 && rotationAngle <= 50);
                  
                  if (currentIsInOBMode && !currentIsOBRotationValid) {
                    // Force window to stay visible if angle remains invalid
                    setShowCarmBox(true);
                  }
                }, 1000);
              }
            }
          }, 3000);
        } else {
          // If rotation angle hasn't changed but is valid and not saved, set a timer to save it
          const isInAPMode = currentRotationAngle >= -20 && currentRotationAngle <= 20;
          
          if (isInAPMode && !isAPRotationSaved) {
            const isAPRotationValid = currentRotationAngle >= -20 && currentRotationAngle <= 20;
            if (isAPRotationValid && !rotationSaveTimerRef.current) {
              rotationSaveTimerRef.current = setTimeout(() => {
                if(stageRef.current === 0){
                setIsAPRotationSaved(true);
                setAPRotationAngle(currentRotationAngle);
                console.log(3)
              }else{
                if (currentRotationAngle === apRotationAngle) setIsAPRotationSaved(true)
              }
              }, 3000);
            }
          } else if (!isInAPMode && !isOBRotationSaved && currentRotationAngle >= -50 && currentRotationAngle <= 50) {
            const isOBRotationValid = 
              (currentRotationAngle >= -50 && currentRotationAngle <= -20) || 
              (currentRotationAngle >= 20 && currentRotationAngle <= 50);
            
            if (isOBRotationValid && !rotationSaveTimerRef.current) {
              rotationSaveTimerRef.current = setTimeout(() => {
                setIsOBRotationSaved(true);
                if(stageRef.current === 0){
                setOBRotationAngle(currentRotationAngle);}
                if(stageRef.current === 1){
                  setOBRotationAngle2(currentRotationAngle);}
              }, 3000);
            }
          }
        }
        
        // If any angle changed, show the carmbox and clear timers
        if (angleChanged || (currentTiltAngle > 20 || currentTiltAngle < -20) || (currentRotationAngle < -50 || currentRotationAngle > 50)) {
          setShowCarmBox(true);
          
          if (carmBoxTimerRef.current) {
            clearTimeout(carmBoxTimerRef.current);
            carmBoxTimerRef.current = null;
          }
        }
        
        setIsProcessing(data.is_processing);
        setProgress(data.progress);
        setVideo_on(data.video_on)
        setImuon(data.imu_on)
        setAi_mode(data.ai_mode)
        
        // Hide carmbox when processing is happening
        if (data.is_processing) {
          setShowCarmBox(false);
          setError(null);
          if (carmBoxTimerRef.current) {
            clearTimeout(carmBoxTimerRef.current);
          }
          if (windowCloseTimerRef.current) {
            clearTimeout(windowCloseTimerRef.current);
          }
        }
        
        if (data.img_count !== previousImgCountRef.current) {
          previousImgCountRef.current = data.img_count;
          await updateImages(data.rotation_angle);
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
      if (tiltSaveTimerRef.current) clearTimeout(tiltSaveTimerRef.current);
      if (rotationSaveTimerRef.current) clearTimeout(rotationSaveTimerRef.current);
      if (windowCloseTimerRef.current) clearTimeout(windowCloseTimerRef.current);
      if (carmBoxTimerRef.current) clearTimeout(carmBoxTimerRef.current);
    };
  }, [isConnected, stage, targetTiltAngle, apRotationAngle, obRotationAngle, obRotationAngle2]);

  const validateTiltAngle = (angle, stage, targetAngle) => {
    if (stage === 0) {
      return angle > -20 && angle <= 20;
    }
    return angle === targetAngle;
  };
  
  const validateRotationAngle = (angle, stage, apRotation, obRotation, obRotation2, activeLeft, activeRight, isCupReg, usedOB) => {
    if (stage === 0) {
      return activeLeft || activeRight;
    }
    
    if (stage === 1) {
      if (activeLeft) {
        return apRotation === angle;
      }
      return ((angle > -50 && angle <= -20) || (angle > 20 && angle <= 50)) && 
             angle * obRotation < 0;
    }
    
    if (isCupReg) {
      return apRotation === angle || angle === usedOB;
    }
    
    if (activeLeft) {
      return apRotation === angle;
    }
    
    return (angle === obRotation) || (angle === obRotation2);
  };
  
  // Update the validation functions that use these helpers
  const isTiltValid = () => validateTiltAngle(angle, stage, targetTiltAngle);
  
  const isRotationValid = () => validateRotationAngle(
    rotationAngle, 
    stage, 
    apRotationAngle, 
    obRotationAngle, 
    obRotationAngle2, 
    activeLeft, 
    activeRight, 
    isCupReg, 
    usedOB
  );

  const isAPRotationValidForMode = (angle) => angle >= -20 && angle <= 20;
const isOBRotationValidForMode = (angle) => 
  (angle >= -50 && angle <= -20) || (angle >= 20 && angle <= 50);

// Replace the duplicate checks with a helper function
const updateRotationSavedState = (currentRotationAngle) => {
  const isInAPMode = isAPRotationValidForMode(currentRotationAngle);
  
  if (isInAPMode) {
    const isAPValid = isAPRotationValidForMode(currentRotationAngle);
    
    if (isAPValid) {
      if (stageRef.current === 0) {
        setIsAPRotationSaved(true);
        setAPRotationAngle(currentRotationAngle);
        console.log(stage, 2);
      } else if (currentRotationAngle === apRotationAngle) {
        setIsAPRotationSaved(true);
      }
    } else {
      setIsAPRotationSaved(false);
      // Re-check logic can be simplified too
      setTimeout(() => {
        const currentIsInAPMode = rotationAngle >= -20 && rotationAngle <= 20;
        const currentIsAPRotationValid = rotationAngle >= -20 && rotationAngle <= 20;
        
        if (currentIsInAPMode && !currentIsAPRotationValid) {
          setShowCarmBox(true);
        }
      }, 1000);
    }
  } else if (currentRotationAngle >= -50 && currentRotationAngle <= 50) {
    const isOBValid = stageRef.current === 0 ? 
      isOBRotationValidForMode(currentRotationAngle) :
      stageRef.current === 1 ?
        isOBRotationValidForMode(currentRotationAngle) && currentRotationAngle * obRotationAngle < 0 :
        (currentRotationAngle === obRotationAngle || currentRotationAngle === obRotationAngle2);
    
    if (isOBValid) {
      setIsOBRotationSaved(true);
      if (stageRef.current === 0) {
        setOBRotationAngle(currentRotationAngle);
      }
      if (stageRef.current === 1) {
        setOBRotationAngle2(currentRotationAngle);
      }
    } else {
      setIsOBRotationSaved(false);
      // Similar re-check logic
      setTimeout(() => {
        const currentIsInOBMode = 
          rotationAngle >= -50 && rotationAngle <= 50 && 
          !(rotationAngle >= -20 && rotationAngle <= 20);
        const currentIsOBRotationValid = isOBRotationValidForMode(rotationAngle);
        
        if (currentIsInOBMode && !currentIsOBRotationValid) {
          setShowCarmBox(true);
        }
      }, 1000);
    }
  }
};


  // Effect to check if angles are valid and adjust saved status if they become invalid
  useEffect(() => {
    
    // If tilt angle becomes invalid, reset its saved status
    if (!isTiltValid() && isTiltSaved) {
      setIsTiltSaved(false);
    }
    
    // For AP rotation angle: must be within [-20, 20] when in AP mode
    if (activeLeft) {
      const isAPRotationValid = rotationAngle >= -20 && rotationAngle <= 20;
      if (!isAPRotationValid && isAPRotationSaved) {
        setIsAPRotationSaved(false);
      }
    }
    
    // For OB rotation angle: must be within [-50, -20] or [20, 50] when in OB mode
    if (activeRight) {
      const isOBRotationValid = 
        (rotationAngle >= -50 && rotationAngle <= -20) || 
        (rotationAngle >= 20 && rotationAngle <= 50);
      if (!isOBRotationValid && isOBRotationSaved) {
        setIsOBRotationSaved(false);
      }
    }
  }, [angle, rotationAngle, activeLeft, activeRight, isTiltSaved, isAPRotationSaved, isOBRotationSaved]);

  // Effect to handle window closing when angles are saved
  useEffect(() => {
    // Don't process if window isn't visible or we're processing
    if (!showCarmBox || isProcessing) {
      return;
    }
    
    
    // Get the appropriate saved state based on current mode
    const isCurrentRotationSaved = activeLeft ? isAPRotationSaved : isOBRotationSaved;
    
    // Check if at least one of the angles has been saved (the other might already be valid)
    const isAtLeastOneAngleSaved = isTiltSaved || isCurrentRotationSaved;
    
    // Check if the unchanged angle (if any) is valid
    const isUnchangedTiltValid = !isTiltSaved && isTiltValid();
    const isUnchangedRotationValid = !isCurrentRotationSaved && isRotationValid();
    
    // Only start close timer if at least one angle is explicitly saved 
    // AND the other angle is either saved OR is in a valid range
    const shouldCloseWindow = 
      (isTiltSaved && (isCurrentRotationSaved || isUnchangedRotationValid)) || 
      (isCurrentRotationSaved && (isTiltSaved || isUnchangedTiltValid));
    
    if (shouldCloseWindow) {
      // Clear any existing window close timer
      if (windowCloseTimerRef.current) {
        clearTimeout(windowCloseTimerRef.current);
      }
      
      // Set a new timer to close the window after 3 seconds
      windowCloseTimerRef.current = setTimeout(() => {
        setShowCarmBox(false);
        
        // Update target angles when window closes
        setTargetTiltAngle(angle);
        
        // Update the appropriate target rotation angle based on current mode
        if (activeLeft) {
          if (stage === 0){
          setAPRotationAngle(rotationAngle);
          console.log(`Target angles saved - Tilt: ${angle}°, AP Rotation: ${rotationAngle}°`);}
        } else {
          if (stage === 0){
          setOBRotationAngle(rotationAngle);
          console.log(`Target angles saved - Tilt: ${angle}°, OB Rotation: ${rotationAngle}°`);}
          if (stage === 1){
            setOBRotationAngle2(rotationAngle);
            console.log(`Target angles saved - Tilt: ${angle}°, OB Rotation 2: ${rotationAngle}°`);}
        }
      }, 3000);
    } else if (windowCloseTimerRef.current && !shouldCloseWindow) {
      // If conditions are no longer met and we have a close timer, clear it
      clearTimeout(windowCloseTimerRef.current);
      windowCloseTimerRef.current = null;
    }
  }, [isTiltSaved, isAPRotationSaved, isOBRotationSaved, angle, rotationAngle, activeLeft, activeRight, showCarmBox, isProcessing]);

  const updateImages = async (currentRotationAngle) => {
    try {
        const response = await fetch('http://localhost:5000/api/image-with-metadata');
        const data = await response.json();
        
        if (currentRotationAngle >= -20 && currentRotationAngle <= 20) {
            setLeftImage(data.image);  // This is now a data URL
            setLeftImageMetadata(data.metadata.metadata);
            setLeftCheckMark(data.checkmark)
            setPelvis((prev) => {
              let tmp = [...prev]
              tmp[0] = data.side
              return tmp
            })
            if (data.checkmark ==2 || data.checkmark==3)setRightCheckMark(data.checkmark)
            setApTaken(currentRotationAngle)
            console.log(data.metadata)
        } else if (currentRotationAngle >= -50 && currentRotationAngle <= 50) {
            setRightImage(data.image);  // This is now a data URL
            setRightImageMetadata(data.metadata.metadata);
            setRightCheckMark(data.checkmark)
            setPelvis((prev) => {
              let tmp = [...prev]
              tmp[1] = data.side
              return tmp
            })
            if (data.checkmark ==2 || data.checkmark==3)setLeftCheckMark(data.checkmark)
            if(stage===0){setObTaken(currentRotationAngle)}
            if(stage===1){setObTaken2(currentRotationAngle)}
        }
        setError(data.error)
        setTiltTaken(targetTiltAngle)
        
        
        console.log(tiltTaken,apTaken,obTaken,obTaken2,targetTiltAngle,apRotationAngle,obRotationAngle,obRotationAngle2)
        setMeasurements(data.measurements)
        if(stage === 2){
          if(data.measurements) setIsCupReg(true)
          if(currentRotationAngle === obRotationAngle) setUsedOB(obRotationAngle)
          if(currentRotationAngle === obRotationAngle2) setUsedOB(obRotationAngle2)
          console.log(usedOB,obRotationAngle,obRotationAngle2)
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
    setTargetTiltAngle(tiltTaken)
    setAPRotationAngle(apTaken)
    setOBRotationAngle(obTaken)
    setOBRotationAngle2(obTaken2)
    console.log(tiltTaken,apTaken,obTaken,obTaken2,targetTiltAngle,apRotationAngle,obRotationAngle,obRotationAngle2,usedOB)
    try {
      await fetch('http://localhost:5000/next', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          'uistates': next ? next : 'prev',
          'stage': st,
          'tiltTaken': tiltTaken,
          'apTaken': apTaken,
          'obTaken': obTaken,
          'obTaken2': obTaken2
        })
      });
    } catch (error) {
      console.error('Error going next:', error);
      setError("Failed to change backend uistate");
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
          body: JSON.stringify({'uistates': showCarmBox || isProcessing || pause ? 'edit' : null})
        });
      } catch (error) {
        console.error('Error setting edit UI state:', error);
        setError("Failed to set UIState");
      }
    };
  
    setEditUIState();
  }, [showCarmBox, isProcessing, pause]);

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
        <L1/>
        
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
          showCarmBox={showCarmBox}
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
      {(!editing&&!(leftImage===require('./AP.png')&&rightImage===require('./OB.png')))&&<L7 handledit={handledit} setReport={setReport} leftCheckMark={leftCheckMark} rightCheckMark={rightCheckMark}/>}


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
      {(!pause && !editing && !isProcessing) && <L9 error={error} measurements={measurements} handlepause={handlepause} moveNext={moveNext} stage={stage}/>}
   
      {/*L10 Carmbox, render if backend angle changes*/}
      {(showCarmBox && !isProcessing) && 
          <L10 
          angle={angle} 
          rotationAngle={rotationAngle} 
          isTiltSaved={isTiltSaved} 
          isRotationSaved={isRotationSaved}
          activeLeft={activeLeft}
          activeRight={activeRight}
          apRotationAngle={apRotationAngle}
          obRotationAngle={obRotationAngle}
          obRotationAngle2={obRotationAngle2}
          isAPRotationSaved={isAPRotationSaved}
          isOBRotationSaved={isOBRotationSaved}
          targetTiltAngle={targetTiltAngle}
          stage={stage}
          isCupReg={isCupReg}
          usedOB={usedOB}
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
          src={require('./IMUConnectionIcon.png')} 
          style={{
            position:'absolute', 
            top:'863px', 
            left:'1825px',
            zIndex:14
          }}
        />
      ):(<img 
        src={require('./IMUerr.png')} 
        style={{
          position:'absolute', 
          top:'864px', 
          left:'1435px',
          animation: 'slideIn 0.5s ease-in-out',
          zIndex:14
        }}
      />)}
      <img 
        src={require('./videoConnectionIcon.png')} 
        style={{position:'absolute', top:'765px', left:'1825px',zIndex:14}}
        onClick={()=>setShowReconnectionPage(!showReconnectionPage)}
      />
      

      {/*L11 Report, render when report button clicked*/}
      {report&&<L11 setReport={setReport} stage={stage} setError={setError}/>}
            
      {/*L12 Pause, render when next button clicked */}
      {<L12 pause={pause} setPause={setPause} handlenext={handlenext}/>}

      {/*L14 Setting, render when setting true*/}
      {setting&&<L14 setSetting={setSetting} ai_mode={ai_mode}/>}

      

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
          cursorPosition={cursorPosition}
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