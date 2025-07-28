import React, { useState, useEffect, useRef } from 'react';

function L2({setShowKeyboard,pid,setting,setSetting,stage,moveNext,handlerestart,handlenext,isCupReg,isTriReg,showCarmBox,autocollect,editing,recon,handlepause,setSelectCup,isProcessing,pause,showReconnectionPage,leftImage,leftImageMetadata,leftSaveRefs,rightImage,rightImageMetadata,rightSaveRefs,measurements,testmeas}) {
  const [switchWarning, setSwitchWarning] = useState(false)
  const [data, setData] = useState({
    'Inclination' : '-',
    'Anteversion' : '-',
    'LLD': '-mm',
    'Offset': '-mm',
  })
  useEffect(() => {
    console.log(testmeas)
    if(testmeas){
      setData(testmeas)
      
      return
    }
    if(stage === 0) setData({
      'Inclination' : '-',
      'Anteversion' : '-',
      'LLD': '-mm',
      'Offset': '-mm',
    })
    else{ setData((prev) => {
      const newMetadata = {...prev};
      if(measurements){
      Object.keys(measurements).forEach((pattern, i) => {
        newMetadata[pattern] = measurements[pattern];
      });}
      console.log(newMetadata)
      return newMetadata;
    })}
  }, [measurements, stage, testmeas]);
  const handleCapture = async () => {
    try {
      const response = await fetch('http://localhost:5000/cap', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({ cap: true }),
      });

      if (!response.ok) {
          throw new Error('Failed to update AI mode');
      }
  } catch (error) {
      console.error('Error updating AI mode:', error);
    }
  }
  const clickDash = () => {
    if(stage === 0){
      if(recon === 2) handlenext()
    }
    if(stage === 1){
      //if(!moveNext) handlerestart()
      if(showDash(stage)[0] === 2) {        
        setSelectCup(true)
        handlepause(stage+1)
      }
    }
    if(stage === 2){
      if(isCupReg) {
        handlepause(stage+1);
        return
      }
      if(leftImageMetadata || leftSaveRefs.current.length === 0 || rightImageMetadata || rightSaveRefs.current.length === 0) setSwitchWarning(true)
      else handlenext('next', true)
    }
    if(stage === 3){
      if(leftImageMetadata || leftSaveRefs.current.length === 0 || rightImageMetadata || rightSaveRefs.current.length === 0) setSwitchWarning(true)
      else handlenext(false, true)
    }
  }
  const clickTriDash = () => {
    setSelectCup(false)
    handlepause(stage+1);
  }

  const blueStage = (stage) =>{
    if(stage === 0) return {'position':'absolute', top:'974px', left:'438px'}
    if(stage === 1) return {'position':'absolute', top:'974px', left:'560px'}
    if(stage === 2) return {'position':'absolute', top:'974px', left:'683px'}
    if(stage === 3) return {'position':'absolute', top:'974px', left:'805px'}
  }
  const showDash = (stage) => {
    if(showCarmBox || editing || isProcessing || pause || showReconnectionPage) return [null, null]
    if(stage === 0){
      if(recon === 2) return [1, {'position':'absolute', top:'974px', left:'560px'}]
      return [null, null]
    }
    if (stage === 1){
      if(moveNext)  return [2, {'position':'absolute', top:'974px', left:'683px'}]
      //return [0, {'position':'absolute', top:'983px', left:'293px'}]
      return [null, null]
    }
    if(stage === 2){
      //if(isCupReg) return [null, null]
      return [3, {'position':'absolute', top:'974px', left:'805px'}]
    }
    if(stage === 3){
      if(isTriReg) return [null, null]
      return [2, {'position':'absolute', top:'974px', left:'683px'}]
    }
  }
    return(
      <>
        {(!autocollect&&!editing) && (
          <>
          <img className="image-button" src={require('./AcquireImageIconBg.png')} alt="acquire icon" style={{position:'absolute', top:'297px', left:'899px', zIndex:7}}/>
          <img className="image-button"  src={require('./AcquireImageIcon.png')} alt="acquire icon" style={{position:'absolute', top:'305px', left:'907px', zIndex:7}} onClick={handleCapture}/>
          </>)
        }

        <img src={require('./CurrentStageBg.png')} style={blueStage(stage)}/>
        {showDash(stage)[0]!==null&&<img src={require('./PossibleStageBg.png')} style={showDash(stage)[1]} onClick={clickDash}/>}
        {showDash(stage)[0]===2&&<img src={require('./PossibleStageBg.png')} style={{'position':'absolute', top:'974px', left:'805px'}} onClick={clickTriDash}/>}
        {(
          stage===0&&recon!==2?<img src={require('./HipIcon1.png')} style={{'position':'absolute', width:'50px', height:'71px', top:'983px', left:'460px', pointerEvents:'none'}}/>:
          <img src={require('./HipIcon2.png')} style={{'position':'absolute', width:'50px', height:'71px', top:'983px', left:'460px', pointerEvents:'none'}}/>
        )}
        {(
          stage===0||(stage===1&&!moveNext)?<img src={require('./HipIcon3.png')} style={{'position':'absolute', width:'50px', height:'71px', top:'983px', left:'582px', pointerEvents:'none'}}/>:
          <img src={require('./HipIcon4.png')} style={{'position':'absolute', width:'50px', height:'71px', top:'983px', left:'582px', pointerEvents:'none'}}/>
        )}
        {(
          isCupReg?<img src={require('./CupIcon2.png')} style={{'position':'absolute', width:'87px', height:'89px', top:'974px', left:'690px', pointerEvents:'none'}}/>:
          <img src={require('./CupIcon1.png')} style={{'position':'absolute', width:'87px', height:'89px', top:'974px', left:'690px', pointerEvents:'none'}}/>
        )}
        {isTriReg?<img src={require('./TrialIcon2.png')} style={{'position':'absolute', width:'60px', height:'65px', top:'987px', left:'826px', pointerEvents:'none'}}/>:
        <img src={require('./TrialIcon1.png')} style={{'position':'absolute', width:'60px', height:'65px', top:'987px', left:'826px', pointerEvents:'none'}}/>
        }
        <div key={Math.random()} style={{position: 'absolute', display: 'flex', flexDirection: 'row', justifyContent:'space-evenly', top:'973px', left: '988px', width: '719px', height: '98px'}}>
          {Object.keys(data).map((column, i) => {
            return (
              <div key={i} style={{display: 'flex', flexDirection: 'column', textAlign:'center', color: 'white', fontFamily:'abel'}}>
                <u style={{fontSize: '38px', color:'#A3A3A3'}}>{column}</u>
                {data[column].includes('mm') ? (
                  <div style={{display: 'flex', flexDirection: 'row', justifyContent:'center'}}>
                    <text style={{fontSize: '36px'}}>{data[column].split('mm')[0]}</text>
                    <div style={{fontSize: '25px'}}>mm</div>
                  </div>
             ) : 
                <text style={{fontSize: '36px'}}>{data[column]}°</text>}
              </div>
            )
          })}
        </div>
        <img src={setting ? require('./SettingIconOn.png') : require('./SettingIcon.png')} style={{'position':'absolute', top:'1016px', left:'1786px'}} onClick={()=>{setSetting(true)}}/>
        
        <input
          type="text"
          value={pid}
          onClick={() => setShowKeyboard(true)}
          style={{
            position: 'absolute',
            left: '64px',
            top: '978px',
            width: '293px',
            background: 'transparent',
            color: 'white',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            border: '0px solid',
            padding: '1px',
            fontSize: '25px',
            fontFamily: 'abel',
            zIndex: 12
          }}
          placeholder="No Patient Data"
        />
        {switchWarning&&<>
          <img src={require('../L10/BgBlur.png')} style={{position:'absolute', top:'0px', zIndex:21, aspectRatio:'1920/1080',height:'1080px'}}/>
          <img src={require('../L21/SwitchAnalysisWindow.png')} style={{'position':'absolute', top:'358px', left:'612px', zIndex:21}}/>
          <img className="image-button" src={require('../L23/YesBtn.png')} style={{'position':'absolute', top:'539px', left:'761px', zIndex:21}} onClick={()=>{handlenext(stage === 3 ? false : 'next', true);setSwitchWarning(false)}}/>
          <img className="image-button" src={require('../L23/NoBtn.png')} style={{'position':'absolute', top:'539px', left:'1035px', zIndex:21}} onClick={()=>{setSwitchWarning(false)}}/>
        </>}
        
        </>
    )
}

export default L2;