import React, { useState, useEffect, useRef } from 'react';
import HipOperationSoftware from './HipOperationSoftware';
import Keyboard from 'react-simple-keyboard';
import 'react-simple-keyboard/build/css/index.css';
function closewin(){
  const remote=(window.require)?window.require('electron').remote:null;
  const w=remote.getCurrentWindow()
  w.close()
}
function App() {
  const [streamActive, setStreamActive] = useState(false);
  const [input, setInput] = useState('');
  const [keyboardVisible, setKeyboardVisible] = useState(false);
  const [layoutName, setLayoutName] = useState("default");
  const [cursorPosition, setCursorPosition] = useState(0);
  const keyboardRef = useRef(null);
  const inputRef = useRef(null);
  const keyboard = useRef(null);

  function startStream(){
    setStreamActive(true);
  };

  function stopStream(){
    setStreamActive(false);
  };
  const onChange = (input) => {
    setInput(input);
  };

  const onKeyboardInput = (key) => {
    const inputElement = inputRef.current;
    const currentInput = input;
    let newInput = currentInput;
    let newCursorPosition = cursorPosition;

    if (key === "{backspace}") {
      if (cursorPosition > 0) {
        newInput = currentInput.slice(0, cursorPosition - 1) + currentInput.slice(cursorPosition);
        newCursorPosition = cursorPosition - 1;
      }
    } else if (key === "{space}") {
      newInput = currentInput.slice(0, cursorPosition) + ' ' + currentInput.slice(cursorPosition);
      newCursorPosition = cursorPosition + 1;
    } else if (key === "{shift}" || key === "{lock}") {
      setLayoutName(layoutName === "default" ? "shift" : "default");
      return;
    } else {
      newInput = currentInput.slice(0, cursorPosition) + key + currentInput.slice(cursorPosition);
      newCursorPosition = cursorPosition + 1;
    }

    setInput(newInput);
    setCursorPosition(newCursorPosition);

    // Set cursor position after state update
    setTimeout(() => {
      inputElement.setSelectionRange(newCursorPosition, newCursorPosition);
    }, 0);
  };

  const handleInputClick = (event) => {
    setCursorPosition(event.target.selectionStart || 0);
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
      <HipOperationSoftware />
      <div className="controls">
        <button onClick={startStream}>Start Stream</button>
        <button onClick={stopStream}>Stop Stream</button>
      </div>
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
            onClick={handleInputClick}
          />
          {keyboardVisible && (
            <div className="keyboard-container" ref={keyboardRef}>
              <Keyboard
                keyboardRef={r => (keyboard.current = r)}
                layoutName={layoutName}
                onKeyPress={onKeyboardInput}
                onChange={onChange}
              />
            </div>
          )}
        </div>
      <button onClick={closewin}>close</button>
    </div>
  );
}

export default App;
