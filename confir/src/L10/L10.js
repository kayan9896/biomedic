import React from 'react';
import GaugeComponent from 'react-gauge-component';

function L10({
  angle, 
  rotationAngle, 
  isTiltSaved, 
  isRotationSaved,
  activeLeft,
  activeRight,
  apRotationAngle,
  obRotationAngle,
  obRotationAngle2,
  isAPRotationSaved,
  isOBRotationSaved,
  targetTiltAngle,
  stage,
  isCupReg,
  usedOB
}) {
  const blue60 = '#3ca4e5';
  const blue80 = '#0260a0';
  const blue10 = '#C3D3E0';
  const blue40 = '#b1cde2';
  const red60 = '#ffa471';
  const red10 = '#EFDACD';
  const red80 = '#cd5445';
  const red40 = '#E9C4BF';

  // Determine if the current rotation angle is valid for the current mode
  const obl = obRotationAngle < -20 ? obRotationAngle : obRotationAngle2;
  const obr = obRotationAngle < -20 ? obRotationAngle2 : obRotationAngle;
  const isAPRotationValid = stage < 2 ? activeLeft : rotationAngle >= (obl+apRotationAngle)/2 && rotationAngle < (obr+apRotationAngle)/2;
  const isOBRotationValid = stage < 2 ? activeRight :
    (rotationAngle > -50 && rotationAngle <= (obl+apRotationAngle)/2) || 
    (rotationAngle > (obr+apRotationAngle)/2 && rotationAngle <= 50);
  
  // Display value for rotation angle (saved or current)
  const getDisplayRotationValue = () => {
    if (stage !== 0 && isAPRotationValid) return `${rotationAngle - apRotationAngle}`
    if (stage !== 0 && stage !== 1 && isOBRotationValid){
      if(!isCupReg) return rotationAngle * obRotationAngle > 0 ? `${rotationAngle - obRotationAngle}` : `${rotationAngle - obRotationAngle2}`
      if(rotationAngle * usedOB > 0) return `${rotationAngle - usedOB}` 
    } 
    return `${rotationAngle}`;
  };
  
  // Color for rotation value display
  const getTiltColor = () => {
    if (stage === 0 && activeLeft && -20 < angle && angle <= 20) return '#46a745'
    if (angle === targetTiltAngle) return '#46a745'
    return '#FFFFFF'
  };
  

  const getRotationColor = () => {
    if (stage === 0 && (activeLeft || activeRight)) return '#46a745'
    if (stage === 1 && ((activeLeft && rotationAngle === apRotationAngle) || (activeRight && rotationAngle * obRotationAngle < 0))) return '#46a745'
    if(stage > 1){
      if (!isCupReg){
        if((rotationAngle === apRotationAngle) || ((rotationAngle === obRotationAngle || rotationAngle === obRotationAngle2))) return '#46a745'
      }else{
        if((rotationAngle === apRotationAngle) || (rotationAngle === usedOB)) return '#46a745'
      }
    }
    return '#FFFFFF'
  };

  const displayValue = (i) => {
    if(i % 1 === 0){
      return [i, 0]
    }
    const str = i.toString().split('.')
    return [str[0], str[1]]
  }

  const getBG = (c, type) => {
    if(type === 'tilt'){
      if(stage === 0 && activeLeft) return c === '#46a745' ? require('./AngleDegreeBg.png') : require('./WhiteAngleDegreeBg.png')
      return c === '#46a745' ? require('./DeltaAngleDegreeBg.png') : require('./WhiteDeltaAngleDegreeBg.png')
    }else{
      if (stage !== 0 && activeLeft) return c === '#46a745' ? require('./DeltaAngleDegreeBg.png') : require('./WhiteDeltaAngleDegreeBg.png')
      if (stage !== 0 && stage !== 1 && activeRight){
        if(isCupReg){
          if((usedOB > 0 && rotationAngle < (obl+apRotationAngle)/2) || (usedOB <= 0 && rotationAngle > (obr+apRotationAngle)/2)){
            return require('./WhiteAngleDegreeBg.png')
          } 
        }
        return c === '#46a745' ? require('./DeltaAngleDegreeBg.png') : require('./WhiteDeltaAngleDegreeBg.png')
      }
      return c === '#46a745' ? require('./AngleDegreeBg.png') : require('./WhiteAngleDegreeBg.png')
    }
  }

  const getTiltTick = () => {
    return [
      {
        value: targetTiltAngle!==null? targetTiltAngle: 0,
        valueConfig:{
          style: {
          fontSize: (angle <= 20 && angle >=-20)? '50px' : '30px',
          fill:'white',
          fontFamily:'abel'
        }},
        lineConfig:{width:(angle <= 20 && angle >= -20)? '5px' : '3px',
          length:(angle <= 20 && angle >= -20)? 20 : 5,
          distanceFromArc: (angle <= 20 && angle >=-20)? 3 : 5,color:'#ffffff'}
      },
      
    ]
  }

  const getRotaionTick = () => {
    if(stage === 0){
      return [
        {
          value: -35,
          valueConfig:{
            style: {
            fontSize: (rotationAngle <= -20 && rotationAngle >=-50)? '50px' : '30px',
            fill:'white',
            fontFamily:'abel'
          }},
          lineConfig:{width:(rotationAngle <= -20 && rotationAngle >=-50)? '5px' : '3px',
            length:(rotationAngle <= -20 && rotationAngle >=-50)? 20 : 5,
            distanceFromArc: (rotationAngle <= -20 && rotationAngle >=-50)? 3 : 5,color:'#ffffff'}
        },
        {
          value: 0,
          valueConfig:{
            style: {
            fontSize: (rotationAngle <= 20 && rotationAngle >-20)? '50px' : '30px',
            fill:'white',
            fontFamily:'abel'
          }},
          lineConfig:{width:(rotationAngle <= 20 && rotationAngle >-20)? '5px' : '3px',
            length:(rotationAngle <= 20 && rotationAngle >-20)? 20 : 5,
            distanceFromArc: (rotationAngle <= 20 && rotationAngle >-20)? 3 : 5,color:'#ffffff'}
        },
        {
          value: 35,
          valueConfig:{
            style: {
            fontSize: (rotationAngle <= 50 && rotationAngle >20) ? '50px' : '30px',
            fill:'white',
            fontFamily:'abel'
          }},
          lineConfig:{width:(rotationAngle <= 50 && rotationAngle >20) ? '5px' : '3px',
            length:(rotationAngle <= 50 && rotationAngle >20) ? 20 : 5,
            distanceFromArc: (rotationAngle <= 50 && rotationAngle >20) ? 3 : 5,color:'#ffffff'}
        }
      ]
    }
    if(stage === 1){
      const array = []
      if(obRotationAngle > 20)(
        array.push(
          {
            value: -35,
            valueConfig:{
              style: {
              fontSize: (rotationAngle <= -20 && rotationAngle >=-50)? '50px' : '30px',
              fill:'white',
              fontFamily:'abel'
            }},
            lineConfig:{width:(rotationAngle <= -20 && rotationAngle >=-50)? '5px' : '3px',
              length:(rotationAngle <= -20 && rotationAngle >=-50)? 20 : 5,
              distanceFromArc: (rotationAngle <= -20 && rotationAngle >=-50)? 3 : 5,color:'#ffffff'}
          }
        )
      )
      array.push({
        value: apRotationAngle!==null? apRotationAngle: 0,
        valueConfig:{
          style: {
          fontSize: (rotationAngle <= 20 && rotationAngle >-20)? '50px' : '30px',
          fill:'white',
          fontFamily:'abel'
        }},
        lineConfig:{width:(rotationAngle <= 20 && rotationAngle >-20)? '5px' : '3px',
          length:(rotationAngle <= 20 && rotationAngle >-20)? 20 : 5,
          distanceFromArc: (rotationAngle <= 20 && rotationAngle >-20)? 3 : 5,color:'#ffffff'}
      })
      if(obRotationAngle < -20){
        array.push({
          value: 35,
          valueConfig:{
            style: {
            fontSize: (rotationAngle <= 50 && rotationAngle >20) ? '50px' : '30px',
            fill:'white',
            fontFamily:'abel'
          }},
          lineConfig:{width:(rotationAngle <= 50 && rotationAngle >20) ? '5px' : '3px',
            length:(rotationAngle <= 50 && rotationAngle >20) ? 20 : 5,
            distanceFromArc: (rotationAngle <= 50 && rotationAngle >20) ? 3 : 5,color:'#ffffff'}
        }
      )}
      return array
    }
    const array = []
    if(!isCupReg || (isCupReg && usedOB <= -20)){
      array.push(
        {
          value: obl,
          valueConfig:{
            style: {
            fontSize: (rotationAngle <= (obl + apRotationAngle)/2 && rotationAngle >=-50)? '50px' : '30px',
            fill:'white',
            fontFamily:'abel'
          }},
          lineConfig:{width:(rotationAngle <= (obl + apRotationAngle)/2 && rotationAngle >=-50)? '5px' : '3px',
            length:(rotationAngle <= (obl + apRotationAngle)/2 && rotationAngle >=-50)? 20 : 5,
            distanceFromArc: (rotationAngle <= (obl + apRotationAngle)/2 && rotationAngle >=-50)? 3 : 5,color:'#ffffff'}
        }
      )
    }
    array.push({
      value: apRotationAngle,
      valueConfig:{
        style: {
        fontSize: (rotationAngle <= (apRotationAngle + obr)/2 && rotationAngle >(obl + apRotationAngle)/2)? '50px' : '30px',
        fill:'white',
        fontFamily:'abel'
      }},
      lineConfig:{width:(rotationAngle <= (apRotationAngle + obr)/2 && rotationAngle >(obl + apRotationAngle)/2)? '5px' : '3px',
        length:(rotationAngle <= (apRotationAngle + obr)/2 && rotationAngle >(obl + apRotationAngle)/2)? 20 : 5,
        distanceFromArc: (rotationAngle <= (apRotationAngle + obr)/2 && rotationAngle >(obl + apRotationAngle)/2)? 3 : 5,color:'#ffffff'}
    })
    if(!isCupReg || (isCupReg && usedOB > 20)){
      array.push({
        value: obr,
        valueConfig:{
          style: {
          fontSize: (rotationAngle <= 50 && rotationAngle >(apRotationAngle + obr)/2) ? '50px' : '30px',
          fill:'white',
          fontFamily:'abel'
        }},
        lineConfig:{width:(rotationAngle <= 50 && rotationAngle >(apRotationAngle + obr)/2) ? '5px' : '3px',
          length:(rotationAngle <= 50 && rotationAngle >(apRotationAngle + obr)/2) ? 20 : 5,
          distanceFromArc: (rotationAngle <= 50 && rotationAngle >(apRotationAngle + obr)/2) ? 3 : 5,color:'#ffffff'}
      })
    }
      return array
  }

  function getTiltArray(targetTiltAngle, angle) {
    if (stage === 0 && activeLeft) return [
      {
        limit: -20,
        color: 'grey',
        showTick: false,
        tooltip: { text: 'Out' }
      },
      {
        limit: 20,
        color: (angle <= 20 && angle >-20) ? red60 : red10,
        showTick: false,
        tooltip: { text: 'AP Range' }
      },
      {
        limit: 90,
        color: 'grey',
        showTick: false,
        tooltip: { text: 'Out' }
      }
    ]


    return [
      {
        limit: -20,
        color: 'grey',
        showTick: false,
        tooltip: { text: 'Out' }
      },
      {
        limit: Math.max(targetTiltAngle - 0.5, -19.99),
        color: red10,
        showTick: false,
        tooltip: { text: 'AP Range' }
      },
      {
        limit: Math.min(targetTiltAngle + 0.5, 19.99),
        color: angle <= 20 && angle > -20 ? red80 : red40,
        showTick: false,
        tooltip: { text: 'AP Range' }
      },
      {
        limit: 20,
        color: red10,
        showTick: false,
        tooltip: { text: 'AP Range' }
      },
      {
        limit: 90,
        color: 'grey',
        showTick: false,
        tooltip: { text: 'Out' }
      }
    ]
  }

  function getDynamicArray() {
    if(stage === 0){
      const array = [
        {
          limit: -50,
          color: 'grey',
          showTick: false,
          tooltip: { text: 'Out' }
        }]
        array.push({
          limit: -20,
          color: (rotationAngle <= -20 && rotationAngle >-50) ? blue60 : blue10,
          showTick: false,
          tooltip: { text: 'OB Range' }
        },)
  
        array.push({
          limit: 20,
          color: rotationAngle <= 20 && rotationAngle > -20 ? red60 : red10,
          showTick: false,
          tooltip: { text: 'AP Range' }
        },)

        array.push({
          limit: 50,
          color: (rotationAngle <= 50 && rotationAngle > 20) ? blue60 : blue10,
          showTick: false,
          tooltip: { text: 'OB Range' }
        },
        {
          limit: 90,
          color: 'grey',
          showTick: false,
          tooltip: { text: 'Out' }
        }
      )
    
      return array;
    }
    if(stage === 1){
      const array = [
        {
          limit: -50,
          color: 'grey',
          showTick: false,
          tooltip: { text: 'Out' }
        }]
        if (obRotationAngle < -20) {
          array.push({
            limit: -20,
            color: 'grey',
            showTick: false,
            tooltip: { text: 'OB Range' }
          },)
        }else{
          array.push({
            limit: -20,
            color: (rotationAngle <= -20 && rotationAngle >-50) ? blue60 : blue10,
            showTick: false,
            tooltip: { text: 'OB Range' }
          },)
        }
        array.push(
          {
            limit: Math.max(apRotationAngle - 0.5, -19.99),
            color: red10,
            showTick: false,
            tooltip: { text: 'AP Range' }
          },
          {
            limit:Math.min(apRotationAngle + 0.5, 19.99),
            color: rotationAngle <= 20 && rotationAngle > -20 ? red80 : red40,
            showTick: false,
            tooltip: { text: 'AP Range' }
          },
        )
        
        array.push({
          limit: 20,
          color: red10,
          showTick: false,
          tooltip: { text: 'AP Range' }
        },)
        if (obRotationAngle > 20) {
          array.push({
            limit: 50,
            color: 'grey',
            showTick: false,
            tooltip: { text: 'OB Range' }
          },)
        }else{
          array.push({
            limit: 50,
            color: (rotationAngle <= 50 && rotationAngle > 20) ? blue60 : blue10,
            showTick: false,
            tooltip: { text: 'OB Range' }
          },)
        }
        array.push(
        {
          limit: 90,
          color: 'grey',
          showTick: false,
          tooltip: { text: 'Out' }
        }
      )
    
      return array;
    }

    const array = [
      {
        limit: -50,
        color: 'grey',
        showTick: false,
        tooltip: { text: 'Out' }
      }]
      
    if(isCupReg && usedOB > 20){
      array.push({
        limit: (obl + apRotationAngle)/2,
        color: 'grey',
        showTick: false,
        tooltip: { text: 'OB Range' }
      },)
    }else{
      console.log((obl + apRotationAngle)/2 - 0.01)
      array.push(
        {
          limit: Math.max(obl - 0.5, -49.99),
          color: blue10,
          showTick: false,
          tooltip: { text: 'OB Range' }
        },
        {
          limit: Math.min(obl + 0.5, (obl + apRotationAngle)/2 - 0.01),
          color: (rotationAngle <= (obl + apRotationAngle)/2 && rotationAngle >-50) ? blue80 : blue40,
          showTick: false,
          tooltip: { text: 'OB Range' }
        },)
      array.push({
        limit: (obl + apRotationAngle)/2,
        color: blue10,
        showTick: false,
        tooltip: { text: 'OB Range' }
      },)
    }
    
    array.push(
      {
        limit: Math.max(apRotationAngle - 0.5, (obl + apRotationAngle)/2 + 0.01),
        color: red10,
        showTick: false,
        tooltip: { text: 'AP Range' }
      },
      {
        limit:Math.min(apRotationAngle + 0.5, (apRotationAngle + obr)/2 - 0.01),
        color: rotationAngle <= (apRotationAngle + obr)/2 && rotationAngle > (obl + apRotationAngle)/2 ? red80 : red40,
        showTick: false,
        tooltip: { text: 'AP Range' }
      },
    )
  
      array.push({
        limit: (apRotationAngle + obr)/2,
        color: red10,
        showTick: false,
        tooltip: { text: 'AP Range' }
      },)

      if(isCupReg && usedOB <= -20){
        array.push({
          limit: 50,
          color: 'grey',
          showTick: false,
          tooltip: { text: 'OB Range' }
        },)
      }else{
      array.push(
        {
          limit: Math.max(obr - 0.5, (apRotationAngle + obr)/2 + 0.01),
          color: blue10,
          showTick: false,
          tooltip: { text: 'OB Range' }
        },
        {
          limit: Math.min(obr + 0.5, 49.99),
          color: (rotationAngle <= 50 && rotationAngle > (apRotationAngle + obr)/2) ? blue80 : blue40,
          showTick: false,
          tooltip: { text: 'OB Range' }
        },
      )
    
      array.push({
        limit: 50,
        color: blue10,
        showTick: false,
        tooltip: { text: 'OB Range' }
      },)}
      array.push({
        limit: 90,
        color: 'grey',
        showTick: false,
        tooltip: { text: 'Out' }
      })
  
    return array;
  }
  console.log(getDynamicArray())
  const deltaDecimal = ()=> {
    if (stage !== 0 && activeLeft) return true
    if (stage !== 0 && stage !== 1 && activeRight){
      if(isCupReg){
        if((usedOB > 0 && rotationAngle < (obl+apRotationAngle)/2) || (usedOB <= 0 && rotationAngle > (obr+apRotationAngle)/2)) return false
      }
      return true
    } 
    return false
  }



  return(
    <>
      <img src={require('./BgBlur.png')} alt="ReportImageViewport" style={{position:'absolute', zIndex:10}}/>
      <div style={{position:'absolute', top:'74px', left:'123px', zIndex:10}}>
        <img src={require('./C-armAgnleAdjustmentWindowBg.png')} alt="box" />
      </div>
      <div style={{position:'absolute',top:'600px',left:'1040'}}>+</div>


      {
        <>
      <GaugeComponent
        type="semicircle"
        style={{position:'absolute',top:'0px', width:'774px',transform:'translate(144.5px,252px)',zIndex:10}}
        marginInPercent={{left: 0, right: 0, top: 0.18, bottom: 0}}
        arc={{
          width: 0.2,
          padding: 0,
          cornerRadius: 1,
          subArcs: getTiltArray(targetTiltAngle, angle)
        }}
        pointer={{
          color: '#ffffff',
          length: 0.1,
          width: 20,
          elastic: false,
          type:'arrow',
          hide:true
        }}
        labels={{
          valueLabel: { hide:true, formatTextValue: value => value + '' },
          tickLabels: {
            type: 'outer',
            hideMinMax: true,
            defaultTickValueConfig: {
              formatTextValue: (value) => {
                
                return 'Tilt';
              },
            },
            ticks: getTiltTick(),
          },
          
        }}
        value={angle}
        minValue={-90}
        maxValue={90}
      />

      <GaugeComponent
        type="semicircle"
        style={{position:'absolute',top:'0px',width:'774px',transform:'translate(929px,252px)',zIndex:10}}
        marginInPercent={{ top: 0.18, bottom: 0.00, left: 0, right: 0 }}
        arc={{
          width: 0.2,
          padding: 0,
          cornerRadius: 1,
          subArcs: getDynamicArray()
        }}
        pointer={{
          color: '#ffffff',
          length: 0.1,
          width: 20,
          elastic: false,
          type:'arrow',
          hide:true
        }}
        labels={{
          valueLabel: { hide:true, formatTextValue: value => value + '' },
          tickLabels: {
            type: 'outer',
            hideMinMax: true,
            defaultTickValueConfig: {
              formatTextValue: (value) => {
                if ((value <= -20 && value >=-50) || (value <= 50 && value >20)) return 'Oblique';
                if (value <= 20 && value >-20) return 'AP';
                return value;
              },
            },
            ticks: getRotaionTick(),
          }
        }}
        value={rotationAngle}
        minValue={-90}
        maxValue={90}
      />
      </>}


      <div className="hand" style={{ 
        transform: `rotate(${angle}deg)`,
        position:'absolute', 
        top:'335px', 
        left:'263px', 
        zIndex:'11' 
      }}>
        <img src={require('./CarmTilt.png')} alt="indicator" />
      </div>
      <div className="hand" style={{ 
        transform: `rotate(${rotationAngle}deg)`,
        position:'absolute', 
        top:'339px', 
        left:'1048px', 
        zIndex:'11' 
      }}>
        <img src={require('./CarmRotation.png')} alt="indicator" />
      </div>
      
      {/* Tilt angle display box */}
      <div style={{position:'absolute', alignItems:'center', top:'666px', left:'376px', zIndex:11}}>
        <img src={getBG(getTiltColor(),'tilt')} alt="box" />
        <div style={{
          position:'absolute', 
          top: 0, 
          right:(stage === 0 && activeLeft)?'148px':'113px', 
          width:'100%', 
          textAlign:'right', 
          color: getTiltColor(),
          fontFamily:'abel', 
          fontSize:'80px'
        }}>
          {displayValue(stage === 0 && activeLeft ? `${angle}` : `${angle - targetTiltAngle}`)[0]}
        </div>
        <div style={{
          position:'absolute', 
          top: 0, 
          left: (stage === 0 && activeLeft)?'179px':'213px', 
          width:'100%', 
          textAlign:'left', 
          color: getTiltColor(),
          fontFamily:'abel', 
          fontSize:'80px'
        }}>
          {displayValue(stage === 0 && activeLeft ? `${angle}` : `${angle - targetTiltAngle}`)[1]}
        </div>

      </div>
      
      {/* Rotation angle display box */}
      <div style={{position:'absolute', top:'666px', left:'1157px', zIndex:11}}>
        <img src={getBG(getRotationColor(),'rot')} alt="box" />
        <div style={{
          position:'absolute', 
          top: 0, 
          right: deltaDecimal()?'113px':'148px', 
          width:'100%', 
          textAlign:'right', 
          color: getRotationColor(),
          fontFamily:'abel', 
          fontSize:'80px'
        }}>
          {displayValue(getDisplayRotationValue())[0]}
        </div>
        <div style={{
          position:'absolute', 
          top: 0, 
          left: deltaDecimal()?'213px':'179px', 
          width:'100%', 
          textAlign:'left', 
          color: getRotationColor(),
          fontFamily:'abel', 
          fontSize:'80px'
        }}>
          {displayValue(getDisplayRotationValue())[1]}
        </div>

      </div>
      {((isTiltSaved) && 
      ((activeLeft && isAPRotationSaved) || (activeRight && isOBRotationSaved))) && 
      <img style={{position:'absolute', top:'671px', left:'900px', zIndex:11}} src={require('./CarmCheckmarks.png')} alt="box" />}
      
    </>
  );
}

export default L10;
