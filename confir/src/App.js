import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import Keyboard from 'react-simple-keyboard';
import 'react-simple-keyboard/build/css/index.css';
import CircularProgress from './CircularProgress';
import PatternDisplay from './PatternDisplay';
import L1 from './L1/L1';
import L2 from './L2/L2';

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
  const imuon = angle >= -45 && angle <= 45;
  const [leftImageMetadata, setLeftImageMetadata] = useState(null);
  const [rightImageMetadata, setRightImageMetadata] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [editing,setEditing] = useState(false)

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

 
  return (
    <div className="app">
      {/*L1 Background*/}
      <L1/>
      
      {/*L2 Status bar*/}
      <L2 onInputChange={onInputChange} setShowKeyboard={setShowKeyboard} onSelect={onSelect} inputRef={inputRef} pid={patient}/>


      {!isConnected ? (
        <div className="connection-container" style={{'position':'absolute'}}>
          {/*L13 Setup, render when iscoonected false*/}
          <img src={require('./SetupWindow.png')} alt="SetupWindow" style={{position:'absolute', top:'21px', left:'255px', zIndex:13}}/>
        
          <button onClick={handleConnect}>Connect</button>
        </div>
      ) : (
        <>{/*L3 Images*/}
          <div className="image-container">
            <div className="image-wrapper">
              <img src={leftImage} alt="Image 1" />
              {/*L5 Viewport select */}
              {activeLeft && (
                <img 
                  src={require('./blueBox.png')} 
                  alt="blue box" 
                  className="blue-box-overlay"
                />
              )}
              {/*L4 Landmarks, rendered when ther is data */}
              {leftImageMetadata && (
            <PatternDisplay metadata={leftImageMetadata} />
          )}
            </div>

            <div className="image-wrapper">
              <img src={rightImage} alt="Image 2" />
              {activeRight && (
                <img 
                  src={require('./blueBox.png')} 
                  alt="blue box" 
                  className="blue-box-overlay"
                />
              )}
              {rightImageMetadata && (
            <PatternDisplay metadata={rightImageMetadata} />
          )}
            </div>
          </div>

      
      
      {/*L6 Edit blur, render when editing true*/}
      {editing&&<img src={require('./EditModeBGBlur.png')} alt="EditModeBGBlur" style={{position:'absolute', top:'0px', left:'960px', zIndex:6}}/>}

      {/*L7 Imaging, render when backend progress=100*/}
      {(!editing&&progress==100)&&<div>
        <img src={require('./Imaging Mode Toolbar.png')} alt="Imaging Mode Toolbar" style={{position:'absolute', top:'458px', left:'921px', zIndex:7}}/>
        <img src={require('./Acquire Image Icon.png')} alt="acquire icon" style={{position:'absolute', top:'660px', left:'899px', zIndex:7}}/>
        <img src={require('./Edit Icon.png')} alt="edit icon" style={{position:'absolute', top:'466px', left:'928px', zIndex:7}} onClick={()=>{setEditing(!editing)}}/>
        <img src={require('./Report Icon.png')} alt="Report Icon" style={{position:'absolute', top:'547px', left:'928px', zIndex:7}}/>
        {/*Show icon based on backend param*/}
        <img src={require('./OB Status Icon.png')} alt="OB Status Icon" style={{position:'absolute', top:'857px', left:'1019px', zIndex:7}}/>
      </div>}


      {/*L8 Edit bar, render when editing true*/}
      {editing&&<div>
        <img src={require('./L8/EditModeBlueBorder.png')} alt="EditModeBlueBorder" style={{position:'absolute', top:'0px', left:'0px', zIndex:7}}/>
        <img src={require('./L8/EditToolbarBg.png')} alt="EditToolbarBg" style={{position:'absolute', top:'239px', left:'920px', zIndex:7}}/>
        <img src={require('./L8/BrightnessIcon.png')} alt="BrightnessIcon" style={{position:'absolute', top:'251px', left:'927px', zIndex:7}} onClick={()=>{setEditing(true)}}/>
        <img src={require('./L8/SaveIcon.png')} alt="SaveIcon" style={{position:'absolute', top:'685px', left:'927px', zIndex:7}}/>
        {/*Show icon based on backend param*/}
        <img src={require('./L8/ExitIcon.png')} alt="ExitIcon" style={{position:'absolute', top:'766px', left:'927px', zIndex:7}} onClick={()=>{setEditing(false)}}/>
      </div>}
          
        
          {/*L9 Message box, render based on backend measurements or error*/}
          {!isRotationInRange && (
            <div className="error-message-overlay">
              <div className="error-message-box">
                Rotation angle out of range. Please adjust the position.
              </div>
            </div>
          )}

        
      
      {/*L10 Carmbox, render if backend angle changes*/}
      {showCarmBox && !isProcessing && (
        <div style={{position:'absolute', top:'82px', left:'337px', zIndex:'10'}}>
          <img src={require('./carmbox.png')} alt="box" />
          <div className="hand" style={{ 
            transform: `rotate(${angle}deg)`,
            position:'absolute', 
            top:'224px', 
            left:'298px', 
            zIndex:'11' 
          }}>
            <img src={require('./tiltcarm.png')} alt="indicator" />
          </div>
          <div className="hand" style={{ 
            transform: `rotate(${rotationAngle}deg)`,
            position:'absolute', 
            top:'220px', 
            left:'750px', 
            zIndex:'11' 
          }}>
            <img src={require('./rotcarm.png')} alt="indicator" />
          </div>
        </div>
      )}
      
      {/*L1x Progree bar, render based on backend params*/}
      {isProcessing && <CircularProgress percentage={progress} />}

      {/*L1x IMU and video icons, render based on backend params */}
      {imuon ? (
        <img 
          src={require('./IMUConnectionIcon.png')} 
          style={{
            position:'absolute', 
            top:'863px', 
            left:'1825px',
            zIndex:12
          }}
        />
      ):(<img 
        src={require('./IMUerr.png')} 
        style={{
          position:'absolute', 
          top:'864px', 
          left:'1435px',
          animation: 'slideIn 0.5s ease-in-out',
          zIndex:12
        }}
      />)}
      <img 
        src={require('./videoConnectionIcon.png')} 
        style={{position:'absolute', top:'765px', left:'1825px',zIndex:12}}
      />
      </>
      )}
      
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
            {/*L11 Report, render when report button clicked*/}

            {/*L12 Pause, render when next button clicked */}

            {/*L13 Setup, render when iscoonected false*/}
          </div>
        )}

    </div>
  );
}

export default App;