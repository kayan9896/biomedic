import React, { useState, useEffect, useRef } from 'react';
import PatternDisplay from './PatternDisplay';

function L3({
  leftImage,
  activeLeft,
  leftImageMetadata,
  rightImage,
  activeRight,
  rightImageMetadata,
  onSaveLeft,
  onSaveRight,
  frameRef,
  editing,
  brightness,
  contrast,
  getInstruction,
  stage,
  recon
}) {

  const leftWrapperRef = useRef(null);
  const rightWrapperRef = useRef(null);

  const [originalGlobal, setOriginalGlobal] = useState(leftImageMetadata ? JSON.parse(JSON.stringify(leftImageMetadata)) : {});
  const [lastSavedGlobal, setLastSavedGlobal] = useState(leftImageMetadata ? JSON.parse(JSON.stringify(leftImageMetadata)) : {});
  const [currentGlobal, setCurrentGlobal] = useState(leftImageMetadata ? JSON.parse(JSON.stringify(leftImageMetadata)) : {});

  const [originalGlobalr, setOriginalGlobalr] = useState(rightImageMetadata ? JSON.parse(JSON.stringify(rightImageMetadata)) : {});
  const [lastSavedGlobalr, setLastSavedGlobalr] = useState(rightImageMetadata ? JSON.parse(JSON.stringify(rightImageMetadata)) : {});
  const [currentGlobalr, setCurrentGlobalr] = useState(rightImageMetadata ? JSON.parse(JSON.stringify(rightImageMetadata)) : {});

  const [resetKey, setResetKey] = useState(0);

  useEffect(() => {
      if(recon < 2) {console.log(leftImageMetadata); setOriginalGlobal(leftImageMetadata ? JSON.parse(JSON.stringify(leftImageMetadata)) : {})}
      setLastSavedGlobal(leftImageMetadata ? JSON.parse(JSON.stringify(leftImageMetadata)) : {});
      setCurrentGlobal(leftImageMetadata ? JSON.parse(JSON.stringify(leftImageMetadata)) : {});
  }, [leftImageMetadata]);

  useEffect(() => {
      if(recon < 2) {console.log(rightImageMetadata); setOriginalGlobalr(rightImageMetadata ? JSON.parse(JSON.stringify(rightImageMetadata)) : {})}
      setLastSavedGlobalr(rightImageMetadata ? JSON.parse(JSON.stringify(rightImageMetadata)) : {});
      setCurrentGlobalr(rightImageMetadata ? JSON.parse(JSON.stringify(rightImageMetadata)) : {});
  }, [rightImageMetadata]);

  useEffect(() => {
      if (onSaveLeft) {
        onSaveLeft({
          getCurrentMetadata: () => {
            return currentGlobal;
          },
          updateSavedMetadata: () => {
            setLastSavedGlobal(JSON.parse(JSON.stringify(currentGlobal)));
          },
          resetToLastSaved: () => {
            console.log("Resetting to last saved state:", lastSavedGlobal);
            setCurrentGlobal(JSON.parse(JSON.stringify(lastSavedGlobal)));
            setResetKey(p => p + 1)
          },
          resetToOriginal: () => {
            console.log("Resetting to original state:", originalGlobal);
            setCurrentGlobal(JSON.parse(JSON.stringify(originalGlobal)));
            setResetKey(p => p + 1)
          },
          setTmp: (template) => {
            console.log("setting template:", template);
            setCurrentGlobal(template);
            setResetKey(p => p + 1)
          },
          checkTmp: () => {
            let allmoved = false;
            Object.values(currentGlobal).forEach((g) => {g.forEach((seg) => {
              allmoved = allmoved || seg['template']
            })})
            return allmoved
          },
          removeRed: () => {
            Object.values(currentGlobal).forEach((g) => {g.forEach((seg) => {
              seg['template'] = 0
            })})
          }
        });
      }
    }, [onSaveLeft, currentGlobal, lastSavedGlobal]);

    useEffect(() => {
      if (onSaveRight) {
        onSaveRight({
          getCurrentMetadata: () => {
            return currentGlobalr;
          },
          updateSavedMetadata: () => {
            setLastSavedGlobalr(JSON.parse(JSON.stringify(currentGlobalr)));
          },
          resetToLastSaved: () => {
            console.log("Resetting to last saved state:", lastSavedGlobalr);
            setCurrentGlobalr(JSON.parse(JSON.stringify(lastSavedGlobalr)));
            setResetKey(p => p + 1)
          },
          resetToOriginal: () => {
            console.log("Resetting to original state:", originalGlobalr);
            setCurrentGlobalr(JSON.parse(JSON.stringify(originalGlobalr)));
            setResetKey(p => p + 1)
          },
          setTmp: (template) => {
            console.log("setting template:", template);
            setCurrentGlobalr(template);
            setResetKey(p => p + 1)
          },
          checkTmp: () => {
            let allmoved = false;
            Object.values(currentGlobalr).forEach((g) => {g.forEach((seg) => {
              allmoved = allmoved || seg['template']
            })})
            return allmoved
          },
          removeRed: () => {
            Object.values(currentGlobalr).forEach((g) => {g.forEach((seg) => {
              seg['template'] = 0
            })})
          }
        });
      }
    }, [onSaveRight, currentGlobalr, lastSavedGlobalr]);
  
  const getFilterStyle = (brightness, contrast) => ({
    filter: `brightness(${brightness}%) contrast(${contrast}%)`,
  });

  const [activeGroup, setActiveGroup] = useState(null)
  
  return(
    <div>
    <div className="image-container" ref={frameRef}>
      <div
        className="image-wrapper"
        ref={leftWrapperRef}
        style={{ position: 'relative' }}
      >
        <img
          src={leftImage}
          alt="Image 1"
          style={{ 
            width: '100%', 
            height: 'auto', 
            ...(leftImage !== getInstruction(stage, 'AP') ? getFilterStyle(brightness[0], contrast[0]) : {})
          }}
        />
        <div className="blue-box-overlay">
        {leftImageMetadata && Object.keys(leftImageMetadata).map((group, i) => (
          <PatternDisplay
          key={i + resetKey}
          group={group}
          fulldata={currentGlobal}
  
          isLeftSquare={true}
          imageUrl={leftImage}
          editing={editing}
          filter = {getFilterStyle(brightness[0], contrast[0])}
          recon={recon}
          activeGroup={activeGroup}
          setActiveGroup={setActiveGroup}
          currentMetadata={group in currentGlobal ? currentGlobal[group] : []}
          setCurrentMetadata={setCurrentGlobal}
          resetKey={0}
        />
        ))}
        </div>
      </div>

      <div
        className="image-wrapper"
        ref={rightWrapperRef}
        style={{ position: 'relative' }}
      >
        <img
          src={rightImage}
          alt="Image 2"
          style={{ 
            width: '100%', 
            height: 'auto', 
            ...((rightImage !== getInstruction(stage, 'OB')) ? getFilterStyle(brightness[1], contrast[1]) : {})
          }}
        />
        
        <div className="blue-box-overlay">
        {rightImageMetadata && Object.keys(rightImageMetadata).map((group, i) => (
          <PatternDisplay
          key={i + resetKey}
          group={group}
          fulldata={currentGlobalr}
  
          isLeftSquare={true}
          imageUrl={rightImage}
          editing={editing}
          filter = {getFilterStyle(brightness[0], contrast[0])}
          recon={recon}
          activeGroup={activeGroup}
          setActiveGroup={setActiveGroup}
          currentMetadata={group in currentGlobalr ? currentGlobalr[group] : []}
          setCurrentMetadata={setCurrentGlobalr}
          resetKey={0}
        />
        ))}
        </div>
      </div>
      <img src={require('./L5/PartingLine.png')} style={{position:'absolute', left: '958px', top: '0px'}}/>

    </div>
        {activeLeft && !editing && (
              <img src={require('./L5/APViewportBlueBorder.png')} alt="blue box" style={{position: 'absolute', top: '0px', left: '0px', zIndex : 4}}/>
            )}
        {activeRight && !editing && (
          <img src={require('./L5/OBViewportBlueBorder.png')} alt="blue box" style={{position: 'absolute', top: '0px', left: '960px', zIndex : 4}}/>
        )}
    </div>
  );
}

export default L3;