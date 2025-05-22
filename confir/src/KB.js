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
    if (activeInput === 'pid' && pidInputRef.current) {
      pidInputRef.current.focus();
      pidInputRef.current.setSelectionRange(localCursorPosition, localCursorPosition);
    } else if (activeInput === 'ratio' && ratioInputRef.current) {
      ratioInputRef.current.focus();
      ratioInputRef.current.setSelectionRange(localCursorPosition, localCursorPosition);
    } else if (activeInput === 'comment' && commentInputRef.current) {
      commentInputRef.current.focus();
      commentInputRef.current.setSelectionRange(localCursorPosition, localCursorPosition);
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
    setLocalCursorPosition(e.target.selectionStart);
  };

  // Handle cursor position updates for any input
  const handleSelect = (e) => {
    setLocalCursorPosition(e.target.selectionStart);
  };

  // Customized keyboard button press handler
  const handleKeyboardButtonPress = (button) => {
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
      setShowKeyboard(false);
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
    } else if (button === "{shift}" || button === "{lock}") {
      setKeyboardLayout(keyboardLayout === "default" ? "shift" : "default");
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
        <img src={require('./L10/BgBlur.png')} alt="ReportImageViewport" style={{position:'absolute', top:'0px', zIndex:10}}/>
        <img src={require('./PatientIDBg.png')} alt="PatientIDBg" style={{position:'absolute', top:'245px', left:'0px', zIndex:13}}/>
        <input
          ref={pidInputRef}
          type="text"
          value={pid}
          onChange={handlePidChange}
          onSelect={handleSelect}
          onClick={() => setActiveInput('pid')}
          style={{
            position: 'absolute',
            left: '374px',
            top: '271px',
            width: '348px',
            height: '71px',
            background: activeInput === 'pid' ? '#fff' : '#eee',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            border: activeInput === 'pid' ? '2px solid #4a90e2' : '0px solid',
            borderRadius: '21px',
            fontSize: '51px',
            fontFamily:'abel',
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
            left: '1457px',
            top: '271px',
            width: '348px',
            height: '71px',
            background: activeInput === 'ratio' ? '#fff' : '#eee',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            border: activeInput === 'ratio' ? '2px solid #4a90e2' : '0px solid',
            borderRadius: '21px',
            fontSize: '51px',
            fontFamily:'abel',
            zIndex: 14
          }}
          placeholder="Ratio"
        />
        
        {/* Comment Input */}
        <input
          ref={commentInputRef}
          value={comment}
          onChange={handleCommentChange}
          onSelect={handleSelect}
          onClick={() => setActiveInput('comment')}
          style={{
            position: 'absolute',
            left: '1154px',
            top: '409px',
            width: '651px',
            height: '71px',
            background: activeInput === 'comment' ? '#fff' : '#eee',
            overflow: 'auto',
            border: activeInput === 'comment' ? '2px solid #4a90e2' : '1px solid #ccc',
            borderRadius: '21px',
            fontSize: '55px',
            fontFamily:'abel',
            zIndex: 14
          }}
          placeholder="Add comment here..."
        />
      
      
      <div 
        ref={keyboardRef}
        style={{
          position: 'absolute',
          left: '0px',
          top: '540px',
          width: '1920px',
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
          onKeyPress={handleKeyboardButtonPress}
          physicalKeyboardHighlight={true}
          mergeDisplay={true}
        />
      </div>

      <img
        src={require('./L13/CrossWhite.png')}
        onClick={() => setShowKeyboard(false)} 
        style={{
          position: 'absolute',
          top: '280px',
          right: '20px',
          zIndex: 1001
        }}
      />
        
    </div>
  );
}

export default KB;