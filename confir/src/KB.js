import React, { useRef, useEffect, useState } from 'react';
import Keyboard from 'react-simple-keyboard';
import 'react-simple-keyboard/build/css/index.css';

function KB({ 
  pid, 
  ratio,
  setRatio,
  comment,
  setComment,
  setPatient,
  setShowKeyboard, 
  keyboardLayout, 
  setKeyboardLayout, 
}) {
  const keyboardRef = useRef(null);
  const pidInputRef = useRef(null);
  const ratioInputRef = useRef(null);
  const commentInputRef = useRef(null);
  
  const [activeInput, setActiveInput] = useState('pid'); // 'pid', 'ratio', or 'comment'
  const [localCursorPosition, setLocalCursorPosition] = useState(null);

  useEffect(() => {
    // Focus the active input when component mounts or active input changes
    console.log(localCursorPosition)
    if (activeInput === 'pid' && pidInputRef.current) {
      pidInputRef.current.selectionStart = localCursorPosition
      pidInputRef.current.selectionEnd = localCursorPosition
      pidInputRef.current.blur();
      pidInputRef.current.focus();
      
      
    } else if (activeInput === 'ratio' && ratioInputRef.current) {
      ratioInputRef.current.selectionStart = localCursorPosition
      ratioInputRef.current.selectionEnd = localCursorPosition
      ratioInputRef.current.blur();
      ratioInputRef.current.focus();
      
    } else if (activeInput === 'comment' && commentInputRef.current) {
      commentInputRef.current.selectionStart = localCursorPosition
      commentInputRef.current.selectionEnd = localCursorPosition
      commentInputRef.current.blur();
      commentInputRef.current.focus();
      
    }
  }, [activeInput, localCursorPosition]);

  // Handle input changes for the ratio field
  const handleRatioChange = (e) => {
    setRatio(e.target.value);
    setLocalCursorPosition(e.target.selectionStart);
  };

  // Handle input changes for the comment field
  const handleCommentChange = (e) => {
    setComment(e.target.value);
    setLocalCursorPosition(e.target.selectionStart);
  };

  // Handle PID input changes but use the local cursor position
  const handlePidChange = (e) => {
    setPatient(e.target.value)
    //setLocalCursorPosition(e.target.selectionStart);
  };

  // Handle cursor position updates for any input
  const handleSelect = (e) => {
    setLocalCursorPosition(e.target.selectionStart);
  };

  // Customized keyboard button press handler
  const handleKeyboardButtonPress = (button, event) => {
    if(event) event.preventDefault()
    let currentValue = '';
    let currentCursorPos = localCursorPosition;
    
    if (activeInput === 'pid') {
      currentValue = pid;
    } else if (activeInput === 'ratio') {
      currentValue = ratio;
    } else if (activeInput === 'comment') {
      currentValue = comment;
    }

    if (button === "{enter}") {
      insertAtCursor('\n');
    } else if (button === "{bksp}") {
      const beforeCursor = currentValue.substring(0, currentCursorPos - 1);
      const afterCursor = currentValue.substring(currentCursorPos);
      const newValue = beforeCursor + afterCursor;
      
      if (activeInput === 'pid') {
        setPatient(newValue)
      } else if (activeInput === 'ratio') {
        setRatio(newValue);
      } else if (activeInput === 'comment') {
        setComment(newValue);
      }
      
      setLocalCursorPosition(currentCursorPos - 1);
    } else if (button === "{space}") {
      insertAtCursor(' ');
    } else if (button === "{lock}" || button === "{shift}") {
      setKeyboardLayout(keyboardLayout === "default" ? "shift" : "default");
    } else if (button === "{tab}") {
      setActiveInput(activeInput === 'pid' ? 'ratio' : activeInput === 'ratio' ? 'comment' : 'pid')
    } else if (button === "←"){
      setLocalCursorPosition(Math.max(0, currentCursorPos - 1));
    } else if (button === "→"){
      setLocalCursorPosition(Math.min(currentValue.length, currentCursorPos + 1));
    } else if (button === "↑"){
      let i = localCursorPosition - 1
      while (i > 0){
        if (currentValue[i] === '\n') break
        i--
      }
      setLocalCursorPosition(i);
    } else if (button === "↓"){
      let i = localCursorPosition + 1
      while (i < currentValue.length){
        if (currentValue[i] === '\n') break
        i++
      }
      setLocalCursorPosition(i);
    } else if (!button.includes("{")) {
      insertAtCursor(button);
    }
  };

  // Helper function to insert text at cursor position
  const insertAtCursor = (str) => {
    let currentValue = '';
    let currentCursorPos = localCursorPosition;
    
    if (activeInput === 'pid') {
      currentValue = pid;
    } else if (activeInput === 'ratio') {
      currentValue = ratio;
    } else if (activeInput === 'comment') {
      currentValue = comment;
    }
    
    const beforeCursor = currentValue.substring(0, currentCursorPos);
    const afterCursor = currentValue.substring(currentCursorPos);
    const newValue = beforeCursor + str + afterCursor;
    
    if (activeInput === 'pid') {
      setPatient(newValue)
    } else if (activeInput === 'ratio') {
      setRatio(newValue);
    } else if (activeInput === 'comment') {
      setComment(newValue);
    }
    
    setLocalCursorPosition(currentCursorPos + str.length);
  };

  return (
      <div>
        <img src={require('./L10/BgBlur.png')} alt="ReportImageViewport" style={{position:'absolute', top:'0px', zIndex:13}} onClick={() => setShowKeyboard(false)}/>
        <img src={require('./PatientIDWindow.png')} alt="PatientIDBg" style={{position:'absolute', top:'310px', left:'0px', zIndex:13}}/>
        <input
          ref={pidInputRef}
          type="text"
          value={pid}
          onChange={handlePidChange}
          onSelect={handleSelect}
          onClick={() => setActiveInput('pid')}
          style={{
            position: 'absolute',
            left: '335px',
            top: '456px',
            width: '401px',
            height: '49px',
            border: activeInput === 'pid' ? '2px solid #fff' : '0px solid',
            backgroundColor: '#131313',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            borderRadius: '20px',
            fontSize: '40px',
            fontFamily:'abel',
            color:'white',
            paddingLeft: '20px',
            paddingRight: '20px',
            zIndex: 14
          }}
          placeholder="No Patient Data"
        />
        {/* Ratio Input */}
        <input
          ref={ratioInputRef}
          type="text"
          value={ratio}
          onChange={handleRatioChange}
          onSelect={handleSelect}
          onClick={() => setActiveInput('ratio')}
          style={{
            position: 'absolute',
            left: '568px',
            top: '571px',
            width: '164px',
            height: '49px',
            backgroundColor: '#131313',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            border: activeInput === 'ratio' ? '2px solid #fff' : '0px solid',
            borderRadius: '20px',
            fontSize: '40px',
            fontFamily:'abel',
            color:'white',
            paddingLeft: '20px',
            paddingRight: '20px',
            zIndex: 14
          }}
          placeholder="Ratio"
        />
        
        {/* Comment Input */}
        <div 
          
          style={{
            position: 'absolute',
            left: '1055px',
            top: '456px',
            width: '687px',
            height: '156px',
            border: activeInput === 'comment' ? '2px solid #fff' : '0px solid',
            borderRadius: '20px',
            backgroundColor: '#131313',
            padding: '4px 20px',

            zIndex: 14
        }}>
        <textarea
          ref={commentInputRef}
          value={comment}
          onChange={handleCommentChange}
          onSelect={handleSelect}
          onClick={() => setActiveInput('comment')}
          style={{
            overflow: 'auto',
            width: '683px',
            height: '156px',
            fontSize: '40px',
            fontFamily:'abel',
            resize: 'none',
            border: 'none',
            backgroundColor: 'transparent',
            color: 'white',

            
          }}
          placeholder="Add comment here..."
        />
        </div>
      
      
      <div 
        ref={keyboardRef}
        style={{
          position: 'absolute',
          left: '178px',
          top: '669px',
          width: '1568px',
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
              "← → {space} ↑ ↓"
            ],
            shift: [
              "~ ! @ # $ % ^ & * ( ) _ + {bksp}",
              "{tab} Q W E R T Y U I O P { } |",
              '{lock} A S D F G H J K L : " {enter}',
              "{shift} Z X C V B N M < > ? {shift}",
              "← → {space} ↑ ↓"
            ]
          }}
          theme={"hg-theme-default myTheme"}
          buttonTheme={[
            {
              class: "hg-black",
              buttons: "` 1 2 3 4 5 6 7 8 9 0 - = {bksp} {tab} q w e r t y u i o p [ ] \\ {lock} a s d f g h j k l ; ' {enter} {shift} z x c v b n m , . / {shift} ← → {space} ↑ ↓"
            },
            {
              class: "hg-space",
              buttons: "{space}"
            },
            {
              class: "hg-shift",
              buttons: "{shift}"
            }
          ]}
          onKeyPress={handleKeyboardButtonPress}
          physicalKeyboardHighlight={true}
          mergeDisplay={true}
          newLineOnEnter={true}
        />
      </div>

      <img
        src={require('./ExitButton.png')}
        onClick={() => setShowKeyboard(false)} 
        style={{
          position: 'absolute',
          top: '346px',
          left: '1841px',
          zIndex: 1001
        }}
      />
        
    </div>
  );
}

export default KB;