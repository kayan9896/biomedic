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

function App() {
  const [angle, setAngle] = useState(0);
  const [patient, setPatient] = useState('');
  const [leftImage, setLeftImage] = useState(require('./AP.png'));
  const [rightImage, setRightImage] = useState(require('./OB.png'));
  const [error, setError] = useState(null);
  const [showKeyboard, setShowKeyboard] = useState(false);
  const keyboardRef = useRef(null);
  const inputRef = useRef(null);
  const [cursorPosition, setCursorPosition] = useState(0);
  const [keyboardLayout, setKeyboardLayout] = useState('default');

  const [showCarmBox, setShowCarmBox] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const previousImgCountRef = useRef(0); 
  const carmBoxTimerRef = useRef(null);
  const [rotationAngle, setRotationAngle] = useState(0);
  const previousRotationAngleRef = useRef(rotationAngle);
  const isInGreenSector = rotationAngle >= -15 && rotationAngle <= 15;
  const isInYellowSector = rotationAngle >= -45 && rotationAngle <= 45;
  const activeLeft = isInGreenSector;
  const activeRight = isInYellowSector && !isInGreenSector;
  const isRotationInRange = isInYellowSector;
  const imuon = angle >= -45 && angle <= 45 ;
  const [leftImageMetadata, setLeftImageMetadata] = useState(null);
  const [rightImageMetadata, setRightImageMetadata] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [editing, setEditing] = useState(false)
  const [report, setReport] = useState(false)
  const [pause, setPause] = useState(false)
  const [setting, setSetting] = useState(false)
  const [measurements, setMeasurements] = useState(null)

  useEffect(() => {
    const fetchStates = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/states');
        const data = await response.json();
        setAngle(data.angle);
        
        // Check if rotation angle has changed
        if (data.rotation_angle !== previousRotationAngleRef.current) {
          setRotationAngle(data.rotation_angle);
          previousRotationAngleRef.current = data.rotation_angle;
          
          // Show carmbox when rotation angle changes
          setShowCarmBox(true);
          
          // Clear any existing timer
          if (carmBoxTimerRef.current) {
            clearTimeout(carmBoxTimerRef.current);
          }
          
          // Set a new timer to hide carmbox after 5 seconds if no further changes
          carmBoxTimerRef.current = setTimeout(() => {
            setShowCarmBox(false);
          }, 5000);
        }
        
        setIsProcessing(data.is_processing);
        setProgress(data.progress);
        
        // Hide carmbox when processing is happening
        if (data.is_processing) {
          setShowCarmBox(false);
          if (carmBoxTimerRef.current) {
            clearTimeout(carmBoxTimerRef.current);
          }
        }
        
        if (data.img_count !== previousImgCountRef.current) {
          previousImgCountRef.current = data.img_count;
          await updateImages(data.rotation_angle);
        }

        if (isRotationInRange) {
          setError(null);
        } else {
          setError("Rotation angle out of range. Please adjust the position.");
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
      if (carmBoxTimerRef.current) {
        clearTimeout(carmBoxTimerRef.current);
      }
    };
  }, [isRotationInRange]);

  const updateImages = async (currentRotationAngle) => {
    try {
        const response = await fetch('http://localhost:5000/api/image-with-metadata');
        const data = await response.json();
        
        if (currentRotationAngle >= -15 && currentRotationAngle <= 15) {
            setLeftImage(data.image);  // This is now a data URL
            setLeftImageMetadata(data.metadata.metadata);
            console.log(data.metadata)
        } else if (currentRotationAngle >= -45 && currentRotationAngle <= 45) {
            setRightImage(data.image);  // This is now a data URL
            setRightImageMetadata(data.metadata.metadata);
        }
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

  const handlenext = async () => {
    setPause(false)
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        showKeyboard &&
        !inputRef.current.contains(event.target) &&
        (!keyboardRef.current || !keyboardRef.current.contains(event.target))
      ) {
        setShowKeyboard(false);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [showKeyboard]);

  const onInputChange = (e) => {
    const value = e.target.value;
    setPatient(value);
    setCursorPosition(e.target.selectionStart);
  };

  const onKeyboardButtonPress = (button) => {
    if (button === "{enter}") {
      setShowKeyboard(false);
    } else if (button === "{bksp}") {
      const beforeCursor = patient.substring(0, cursorPosition - 1);
      const afterCursor = patient.substring(cursorPosition);
      setPatient(beforeCursor + afterCursor);
      setCursorPosition(cursorPosition - 1);
    } else if (button === "{space}") {
      insertAtCursor(' ');
    } else if (button === "{shift}"||button === "{lock}") {
      setKeyboardLayout(keyboardLayout === "default" ? "shift" : "default");
    } else if (!button.includes("{")) {
      insertAtCursor(button);
    }
  
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };
  const insertAtCursor = (str) => {
    const beforeCursor = patient.substring(0, cursorPosition);
    const afterCursor = patient.substring(cursorPosition);
    const newValue = beforeCursor + str + afterCursor;
    setPatient(newValue);
    setCursorPosition(cursorPosition + str.length);
  };

  // Update cursor position when input is focused or clicked
  const onSelect = (e) => {
    setCursorPosition(e.target.selectionStart);
  };

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.setSelectionRange(cursorPosition, cursorPosition);
    }
  }, [cursorPosition, patient]);

  const leftSaveRef = useRef({});
  const rightSaveRef = useRef({});

  // Save handler - sends updated data to backend
  const handleSave = async () => {
    try {
      // Get current metadata from both pattern displays
      const leftData = leftSaveRef.current && typeof leftSaveRef.current.getCurrentMetadata === 'function' 
        ? leftSaveRef.current.getCurrentMetadata() 
        : leftImageMetadata;
      
      const rightData = rightSaveRef.current && typeof rightSaveRef.current.getCurrentMetadata === 'function' 
        ? rightSaveRef.current.getCurrentMetadata() 
        : rightImageMetadata;
      
      // Send to backend
      await fetch('http://localhost:5000/landmarks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          leftMetadata: leftData,
          rightMetadata: rightData
        }),
      });
      
      // Exit edit mode after successful save
      setEditing(false);
    } catch (error) {
      console.error('Error saving landmarks:', error);
      setError("Failed to save landmarks");
    }
  };

  // Exit handler - reverts to original positions without saving
  const handleExit = () => {
    // Reset both pattern displays to original state
    if (leftSaveRef.current.resetToOriginal) {
      leftSaveRef.current.resetToOriginal();
    }
    if (rightSaveRef.current.resetToOriginal) {
      rightSaveRef.current.resetToOriginal();
    }
    setEditing(false);
  };

  return (
    <div className="app">
      {/*L1 Background*/}
      <L1/>
      
      {/*L2 Status bar*/}
      <L2 onInputChange={onInputChange} setShowKeyboard={setShowKeyboard} onSelect={onSelect} inputRef={inputRef} pid={patient} setSetting={setSetting} setting={setting}/>


      {!isConnected ? (
        <div>
          {/*L13 Setup, render when iscoonected false*/}
          <L13 handleConnect={handleConnect}/>  
        </div>
      ) : (
        <>
        {/*L3 Images, containing L4 landmarks and L5 viewport inside*/}
        <L3 
        leftImage={leftImage} 
        activeLeft={activeLeft} 
        leftImageMetadata={leftImageMetadata} 
        rightImage={rightImage}
        activeRight={activeRight}
        rightImageMetadata={rightImageMetadata}
        onSaveLeft={leftSaveRef}
        onSaveRight={rightSaveRef}
      />
      
      
      {/*L6 Edit blur, render when editing true*/}
      <L6 editableSide={editing} setEditing={setEditing}/>

      {/*L7 Imaging, render when backend progress=100*/}
      {(!editing&&progress===100)&&<L7 setEditing={setEditing} setReport={setReport}/>}


      {/*L8 Edit bar, render when editing true*/}
      {editing && <L8 setEditing={setEditing} onSave={handleSave} onExit={handleExit} />}
          
        
      {/*L9 Message box, render based on backend measurements or error*/}
      {(!pause && (error || measurements)) && <L9 error={error} measurements={measurements} setPause={setPause}/>}
   
      {/*L10 Carmbox, render if backend angle changes*/}
      {(showCarmBox && !isProcessing) && <L10 angle={angle} rotationAngle={rotationAngle}/>}

      {/*L1x IMU and video icons, render based on backend params */}
      {imuon ? (
        <img 
          src={require('./IMUConnectionIcon.png')} 
          style={{
            position:'absolute', 
            top:'863px', 
            left:'1825px',
            zIndex:10
          }}
        />
      ):(<img 
        src={require('./IMUerr.png')} 
        style={{
          position:'absolute', 
          top:'864px', 
          left:'1435px',
          animation: 'slideIn 0.5s ease-in-out',
          zIndex:10
        }}
      />)}
      <img 
        src={require('./videoConnectionIcon.png')} 
        style={{position:'absolute', top:'765px', left:'1825px',zIndex:10}}
      />
      </>
      )}

      {/*L11 Report, render when report button clicked*/}
      {report&&<L11 setReport={setReport}/>}
            
      {/*L12 Pause, render when next button clicked */}
      {pause&&<L12 setPause={setPause} setReport={setReport} handlenext={handlenext}/>}
      
      {/*L13 Setup, render when iscoonected false*/}

      {/*L14 Setting, render when setting true*/}
      {setting&&<L14/>}

      {/*L1x Progree bar, render based on backend params*/}
      {isProcessing && <CircularProgress percentage={progress} />}
      
      {/*L1x Keyboard, render when showKeyboard true*/}
      {showKeyboard && (
          <div 
            ref={keyboardRef}
            style={{
              position: 'absolute',
              left: '30px',
              top: '740px',
              width: '750px',
              zIndex: 1000
            }}
          >
            <Keyboard
              layoutName={keyboardLayout}
              layout={{
                default: [
                  "` 1 2 3 4 5 6 7 8 9 0 - = {bksp}",
                  "{tab} q w e r t y u i o p [ ] \\",
                  "{lock} a s d f g h j k l ; ' {enter}",
                  "{shift} z x c v b n m , . / {shift}",
                  "{space}"
                ],
                shift: [
                  "~ ! @ # $ % ^ & * ( ) _ + {bksp}",
                  "{tab} Q W E R T Y U I O P { } |",
                  '{lock} A S D F G H J K L : " {enter}',
                  "{shift} Z X C V B N M < > ? {shift}",
                  "{space}"
                ]
              }}
               
              theme={"hg-theme-default myTheme"}
              buttonTheme={[
                {
                  class: "hg-black",
                  buttons: "` 1 2 3 4 5 6 7 8 9 0 - = {bksp} {tab} q w e r t y u i o p [ ] \\ {lock} a s d f g h j k l ; ' {enter} {shift} z x c v b n m , . / {shift} {space}"
                }
              ]}
              onKeyPress={onKeyboardButtonPress}
            />
          </div>
        )}
  

    </div>
  );
}

export default App;