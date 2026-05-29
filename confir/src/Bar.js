import React, {useEffect, useState} from 'react';

const Bar = ({stage, setStage}) => {
    const titles = ['SETUP system', 'SCAN preop', 'CUP assessment', 'TRIAL assessment', 'Closing']
    return (
      <div style={{position: 'fixed', height: '5vh', width: '100vw', backgroundColor: "white", display:'flex', flexDirection:'row', zIndex: 24}}>
        {titles.map((item, index) => {
          return <Step highlight={stage === index} arrow={index < titles.length - 1} title={item} fclick={() => {setStage(index)}}/>
        })}
      </div>
    );
}

const Step = ({highlight, arrow, title, fclick}) => {

  return (
    <div style={{backgroundColor: highlight ? "deepskyblue" : "white", width: "20vw", display:'flex', alignItems: 'center'}} onClick={fclick}>
      <div style={{width: '20vw', textAlign: 'center', fontWeight:'bold'}}>{title}</div>
      {arrow && <div style={{backgroundColor: highlight ? "deepskyblue" : "white", height: '3.6vh', width: '3.6vh', borderTop: '2px solid black', borderRight: '2px solid black', transform: 'translateX(1.8vh) rotate(45deg) '}}></div>}
    </div>
  );
};

export default Bar;