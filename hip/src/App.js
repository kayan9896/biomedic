import React, { useState, useEffect, useRef } from 'react';
import Keyboard from 'react-simple-keyboard';
import 'react-simple-keyboard/build/css/index.css';
import './App.css';

function App() {
  const [streamActive, setStreamActive] = useState(false);
  const [input, setInput] = useState('');
  const [keyboardVisible, setKeyboardVisible] = useState(false);
  const [layoutName, setLayoutName] = useState("default");
  const keyboardRef = useRef(null);
  const inputRef = useRef(null);
  const keyboard = useRef();

  const startStream = () => {
    setStreamActive(true);
  };

  const stopStream = () => {
    setStreamActive(false);
  };

  const onKeyboardInput = (key, e) => {
    let currentInput = input;

    if (key === "{backspace}") {
      currentInput = currentInput.slice(0, -1);
    } else if (key === "{space}") {
      currentInput += ' ';
    } else if (key === "{shift}" || key === "{lock}") {
      setLayoutName(layoutName === "default" ? "shift" : "default");
      return;
    } else {
      currentInput += key;
    }

    setInput(currentInput);
  };

  const onChangeInput = (event) => {
    setInput(event.target.value);
  };

  const handleInputFocus = () => {
    setKeyboardVisible(true);
  };

  const handleClickOutside = (event) => {
    if (keyboardRef.current && 
        !keyboardRef.current.contains(event.target) &&
        !inputRef.current.contains(event.target)) {
      setKeyboardVisible(false);
    }
  };

  useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div className="App">
      <h1>Camera Stream</h1>
      <div className="controls">
        <button onClick={startStream}>Start Stream</button>
        <button onClick={stopStream}>Stop Stream</button>
      </div>
      <div className="content-container">
        {streamActive && (
          <div className="video-container">
            <img
              src="http://localhost:5000/video_feed"
              alt="Camera Stream"
              style={{ maxWidth: '100%', height: 'auto' }}
            />
          </div>
        )}
        <div className="input-container">
          <input
            ref={inputRef}
            value={input}
            placeholder="Type here..."
            onFocus={handleInputFocus}
            onChange={onChangeInput}
          />
          {keyboardVisible && (
            <div className="keyboard-container" ref={keyboardRef}>
              <Keyboard
                keyboardRef={r => (keyboard.current = r)}
                layoutName={layoutName}
                onKeyPress={onKeyboardInput}
                layout={{
                  default: [
                    "1 2 3 4 5 6 7 8 9 0",
                    "q w e r t y u i o p",
                    "a s d f g h j k l",
                    "{shift} z x c v b n m {backspace}",
                    ".com @ {space}"
                  ],
                  shift: [
                    "1 2 3 4 5 6 7 8 9 0",
                    "Q W E R T Y U I O P",
                    "A S D F G H J K L",
                    "{shift} Z X C V B N M {backspace}",
                    ".com @ {space}"
                  ]
                }}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;