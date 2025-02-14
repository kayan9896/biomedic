import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import Keyboard from 'react-simple-keyboard';
import 'react-simple-keyboard/build/css/index.css';

function App() {
  const [angle, setAngle] = useState(0);
  const [manualAngle, setManualAngle] = useState('');
  const [leftImage, setLeftImage] = useState(require('./AP.png'));
  const [rightImage, setRightImage] = useState(require('./OB.png'));
  const [error, setError] = useState(null);
  const [showCarmBox, setShowCarmBox] = useState(true);
  const [showKeyboard, setShowKeyboard] = useState(false);
  const keyboardRef = useRef(null);
  const inputRef = useRef(null);
  const [cursorPosition, setCursorPosition] = useState(0);
  const [keyboardLayout, setKeyboardLayout] = useState('default');

  const [isConnected, setIsConnected] = useState(false);
  const previousImgCountRef = useRef(0); 
  const [rotationAngle, setRotationAngle] = useState(0);
  const isInGreenSector = rotationAngle >= -15 && rotationAngle <= 15;
  const isInYellowSector = rotationAngle >= -45 && rotationAngle <= 45;
  const activeLeft = isInGreenSector;
  const activeRight = isInYellowSector && !isInGreenSector;
  const isRotationInRange = isInYellowSector;
  const imuon = angle >= -45 && angle <= 45;

  useEffect(() => {
    const fetchStates = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/states');
        const data = await response.json();
        setAngle(data.angle);
        setRotationAngle(data.rotation_angle);
        
        if (data.img_count !== previousImgCountRef.current) {
          previousImgCountRef.current = data.img_count;
          await updateImages(data.rotation_angle);
          setShowCarmBox(false);
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
    return () => clearInterval(intervalId);
  }, []);

  const updateImages = async (currentRotationAngle) => {
    try {
      const response = await fetch('http://localhost:5000/api/latest-image');
      const imageBlob = await response.blob();
      const imageUrl = URL.createObjectURL(imageBlob);

      if (currentRotationAngle >= -15 && currentRotationAngle <= 15) {
        setLeftImage(imageUrl);
      } else if (currentRotationAngle >= -45 && currentRotationAngle <= 45) {
        setRightImage(imageUrl);
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
    setManualAngle(value);
    setCursorPosition(e.target.selectionStart);
  };

  const onKeyboardButtonPress = (button) => {
    if (button === "{enter}") {
      setShowKeyboard(false);
    } else if (button === "{bksp}") {
      const beforeCursor = manualAngle.substring(0, cursorPosition - 1);
      const afterCursor = manualAngle.substring(cursorPosition);
      setManualAngle(beforeCursor + afterCursor);
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
    const beforeCursor = manualAngle.substring(0, cursorPosition);
    const afterCursor = manualAngle.substring(cursorPosition);
    const newValue = beforeCursor + str + afterCursor;
    setManualAngle(newValue);
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
  }, [cursorPosition, manualAngle]);

 
  return (
    <div className="app">
      <img src={require('./background.png')} style={{'position':'absolute'}}/>
      {!isConnected ? (
        <div className="connection-container" style={{'position':'absolute'}}>
          <button onClick={handleConnect}>Connect</button>
        </div>
      ) : (
        <>
          <div className="image-container">
            <div className="image-wrapper">
              <img src={leftImage} alt="Image 1" />
              {activeLeft && (
                <img 
                  src={require('./blueBox.png')} 
                  alt="blue box" 
                  className="blue-box-overlay"
                />
              )}
              <div className="circle-mask"></div>
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
              <div className="circle-mask"></div>
            </div>
          </div>
          
          {/* New angle input box */}
          <input
          ref={inputRef}
          type="text"
          value={manualAngle}
          onChange={onInputChange}
          onClick={() => setShowKeyboard(true)}
          onSelect={onSelect}
          style={{
            position: 'absolute',
            left: '50px',
            top: '995px',
            width: '180px',
            background: 'black',
            color: 'white',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            border: '1px solid white',
            padding: '8px',
            fontSize: '16px'
          }}
          placeholder="no patient data"
        />
        
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

          {!isRotationInRange && (
            <div className="error-message-overlay">
              <div className="error-message-box">
                Rotation angle out of range. Please adjust the position.
              </div>
            </div>
          )}

          {/* {!imuon && (
            <div className="sliding-error" style={{
              position: 'absolute',
              right: '-300px',
              top: '863px',
              animation: 'slideIn 0.5s forwards',
              backgroundColor: '#ff4444',
              padding: '10px',
              borderRadius: '5px',
              color: 'white',
              zIndex: 1000
            }}>
              IMU Disconnected
            </div>
          )} */}
        </>
      )}
      
      {showCarmBox && (
        <div style={{position:'absolute', top:'82px', left:'337px', zIndex:'2'}}>
          <img src={require('./carmbox.png')} alt="box" />
          <div className="hand" style={{ 
            transform: `rotate(${angle}deg)`,
            position:'absolute', 
            top:'224px', 
            left:'298px', 
            zIndex:'3' 
          }}>
            <img src={require('./tiltcarm.png')} alt="indicator" />
          </div>
          <div className="hand" style={{ 
            transform: `rotate(${rotationAngle}deg)`,
            position:'absolute', 
            top:'220px', 
            left:'750px', 
            zIndex:'3' 
          }}>
            <img src={require('./rotcarm.png')} alt="indicator" />
          </div>
        </div>
      )}
      
      {imuon ? (
        <img 
          src={require('./IMUConnectionIcon.png')} 
          style={{
            position:'absolute', 
            top:'863px', 
            left:'1825px'
          }}
        />
      ):(<img 
        src={require('./IMUerr.png')} 
        style={{
          position:'absolute', 
          top:'864px', 
          left:'1435px',
          animation: 'slideIn 0.5s ease-in-out',
        }}
      />)}
      <img 
        src={require('./videoConnectionIcon.png')} 
        style={{position:'absolute', top:'765px', left:'1825px'}}
      />
    </div>
  );
}

export default App;