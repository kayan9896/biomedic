import React from 'react';
import GaugeComponent from 'react-gauge-component';

function L10({
  tiltAngle, 
  rotationAngle, 
  activeLeft,
  activeRight,
  apRotationAngle,
  obRotationAngle,
  obRotationAngle2,
  targetTiltAngle,
  stage,
  isCupReg,
  usedOB,
  showIcon,
  tiltValid,
  rotValid,
  obl,
  obr,
  tiltl,
  tiltr,
  apl,
  apr,
  rangel,
  ranger,
  scale,
  applyTarget
}) {
  const blue60 = '#3ca4e5';
  const blue80 = '#0260a0';
  const blue10 = '#C3D3E0';
  const blue40 = '#b1cde2';
  const red60 = '#ffa471';
  const red10 = '#EFDACD';
  const red80 = '#cd5445';
  const red40 = '#E9C4BF';
  
  // Display value for rotation tiltAngle (saved or current)
  const getDisplayRotationValue = () => {
    if (stage !== 0 && activeLeft) return [`${rotationAngle - apRotationAngle}`, 1]
    if (stage !== 0 && stage !== 1 && activeRight){
      if(!isCupReg) return rotationAngle * obRotationAngle > 0 ? [`${rotationAngle - obRotationAngle}`, 1] : [`${rotationAngle - obRotationAngle2}`, 1]
      if(rotationAngle * usedOB > 0) return [`${rotationAngle - usedOB}`, 1]
    } 
    if (activeLeft && apRotationAngle) return [`${rotationAngle - apRotationAngle}`, 1]
    if (activeRight && obRotationAngle && rotationAngle * obRotationAngle > 0) return [`${rotationAngle - obRotationAngle}`, 1] 
    if (activeRight && obRotationAngle2 && rotationAngle * obRotationAngle2 > 0) return [`${rotationAngle - obRotationAngle2}`, 1]
    return [`${rotationAngle}`, 0];
  };

  const getDisplayTiltValue = () => {
    return stage === 0 && activeLeft && !applyTarget ? [`${tiltAngle}`, 0] : [`${tiltAngle - targetTiltAngle}`, 1]
  };
  
  // Color for rotation value display
  const getTiltColor = () => {
    if (tiltValid) return '#46a745'
    return '#FFFFFF'
  };
  
  const getRotationColor = () => {
    if (rotValid) return '#46a745'
    return '#FFFFFF'
  };

  const displayValue = (i) => {
    const str = parseFloat(i).toFixed(1).split('.')
    return [str[0], str[1]]
  }

  const getBG = (c, delta) => {
    if (!delta) return c === '#46a745' ? require('./AngleDegreeBg.png') : require('./WhiteAngleDegreeBg.png')
    return c === '#46a745' ? require('./DeltaAngleDegreeBg.png') : require('./WhiteDeltaAngleDegreeBg.png')
  }

  const getTiltTick = () => {
    return [
      {
        value: targetTiltAngle!==null? targetTiltAngle: 0,
        valueConfig:{
          style: {
          fontSize: (tiltAngle <= tiltr && tiltAngle >= tiltl)? '50px' : '30px',
          fill:'white',
          fontFamily:'abel'
        }},
        lineConfig:{width:(tiltAngle <= tiltr && tiltAngle >= tiltl)? '5px' : '3px',
          length:(tiltAngle <= tiltr && tiltAngle >= tiltl)? 20 : 5,
          distanceFromArc: (tiltAngle <= tiltr && tiltAngle >= tiltl)? 3 : 5,color:'#ffffff'}
      },
      
    ]
  }

  const getRotaionTick = () => {
    if(stage === 0){
      let targetl = null
      let targetr = null
      if (obRotationAngle !== null){
        if(obRotationAngle < 0) targetl = obRotationAngle
        else targetr = obRotationAngle
      } 
      if (obRotationAngle2 !== null){
        if(obRotationAngle2 < 0) targetl = obRotationAngle2
        else targetr = obRotationAngle2
      } 
      return [
        {
          value: targetl === null ? -(apr + ranger)/2 : targetl,
          valueConfig:{
            style: {
            fontSize: (rotationAngle <= apl && rotationAngle > rangel)? '50px' : '30px',
            fill:'white',
            fontFamily:'abel'
          }},
          lineConfig:{width:(rotationAngle <= apl && rotationAngle > rangel)? '5px' : '3px',
            length:(rotationAngle <= apl && rotationAngle > rangel)? 20 : 5,
            distanceFromArc: (rotationAngle <= apl && rotationAngle > rangel)? 3 : 5,color:'#ffffff'}
        },
        {
          value: apRotationAngle === null ? 0 : apRotationAngle,
          valueConfig:{
            style: {
            fontSize: (rotationAngle <= apr && rotationAngle > apl)? '50px' : '30px',
            fill:'white',
            fontFamily:'abel'
          }},
          lineConfig:{width:(rotationAngle <= apr && rotationAngle > apl)? '5px' : '3px',
            length:(rotationAngle <= apr && rotationAngle > apl)? 20 : 5,
            distanceFromArc: (rotationAngle <= apr && rotationAngle > apl)? 3 : 5,color:'#ffffff'}
        },
        {
          value: targetr === null ? (apr + ranger)/2 : targetr,
          valueConfig:{
            style: {
            fontSize: (rotationAngle <= ranger && rotationAngle > apr) ? '50px' : '30px',
            fill:'white',
            fontFamily:'abel'
          }},
          lineConfig:{width:(rotationAngle <= ranger && rotationAngle > apr) ? '5px' : '3px',
            length:(rotationAngle <= ranger && rotationAngle > apr) ? 20 : 5,
            distanceFromArc: (rotationAngle <= ranger && rotationAngle > apr) ? 3 : 5,color:'#ffffff'}
        }
      ]
    }
    if(stage === 1){
      const array = []
      if(obRotationAngle > apr)(
        array.push(
          {
            value: obRotationAngle2 === null ? -(apr + ranger)/2 : obRotationAngle2,
            valueConfig:{
              style: {
              fontSize: (rotationAngle <= apl && rotationAngle > rangel)? '50px' : '30px',
              fill:'white',
              fontFamily:'abel'
            }},
            lineConfig:{width:(rotationAngle <= apl && rotationAngle > rangel)? '5px' : '3px',
              length:(rotationAngle <= apl && rotationAngle > rangel)? 20 : 5,
              distanceFromArc: (rotationAngle <= apl && rotationAngle > rangel)? 3 : 5,color:'#ffffff'}
          }
        )
      )
      array.push({
        value: apRotationAngle!==null? apRotationAngle: 0,
        valueConfig:{
          style: {
          fontSize: (rotationAngle <= apr && rotationAngle > apl)? '50px' : '30px',
          fill:'white',
          fontFamily:'abel'
        }},
        lineConfig:{width:(rotationAngle <= apr && rotationAngle > apl)? '5px' : '3px',
          length:(rotationAngle <= apr && rotationAngle > apl)? 20 : 5,
          distanceFromArc: (rotationAngle <= apr && rotationAngle > apl)? 3 : 5,color:'#ffffff'}
      })
      if(obRotationAngle < apl){
        array.push({
          value: obRotationAngle2 === null ? (apr + ranger)/2 : obRotationAngle2,
          valueConfig:{
            style: {
            fontSize: (rotationAngle <= ranger && rotationAngle > apr) ? '50px' : '30px',
            fill:'white',
            fontFamily:'abel'
          }},
          lineConfig:{width:(rotationAngle <= ranger && rotationAngle > apr) ? '5px' : '3px',
            length:(rotationAngle <= ranger && rotationAngle > apr) ? 20 : 5,
            distanceFromArc: (rotationAngle <= ranger && rotationAngle > apr) ? 3 : 5,color:'#ffffff'}
        }
      )}
      return array
    }
    const array = []
    if(!isCupReg || (isCupReg && usedOB <= apl)){
      array.push(
        {
          value: obl,
          valueConfig:{
            style: {
            fontSize: (rotationAngle <= (obl + apRotationAngle)/2 && rotationAngle > rangel)? '50px' : '30px',
            fill:'white',
            fontFamily:'abel'
          }},
          lineConfig:{width:(rotationAngle <= (obl + apRotationAngle)/2 && rotationAngle > rangel)? '5px' : '3px',
            length:(rotationAngle <= (obl + apRotationAngle)/2 && rotationAngle > rangel)? 20 : 5,
            distanceFromArc: (rotationAngle <= (obl + apRotationAngle)/2 && rotationAngle > rangel)? 3 : 5,color:'#ffffff'}
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
    if(!isCupReg || (isCupReg && usedOB > apr)){
      array.push({
        value: obr,
        valueConfig:{
          style: {
          fontSize: (rotationAngle <= ranger && rotationAngle >(apRotationAngle + obr)/2) ? '50px' : '30px',
          fill:'white',
          fontFamily:'abel'
        }},
        lineConfig:{width:(rotationAngle <= ranger && rotationAngle >(apRotationAngle + obr)/2) ? '5px' : '3px',
          length:(rotationAngle <= ranger && rotationAngle >(apRotationAngle + obr)/2) ? 20 : 5,
          distanceFromArc: (rotationAngle <= ranger && rotationAngle >(apRotationAngle + obr)/2) ? 3 : 5,color:'#ffffff'}
      })
    }
      return array
  }

  function getTiltArray(targetTiltAngle, tiltAngle) {
    if (stage === 0 && activeLeft && (targetTiltAngle == null || (targetTiltAngle !== null && !applyTarget))) return [
      {
        limit: apl,
        color: 'grey',
        showTick: false,
        tooltip: { text: 'Out' }
      },
      {
        limit: apr,
        color: (tiltAngle <= tiltr && tiltAngle >apl) ? red60 : red10,
        showTick: false,
        tooltip: { text: 'AP Range' }
      },
      {
        limit: 90*scale,
        color: 'grey',
        showTick: false,
        tooltip: { text: 'Out' }
      }
    ]


    return [
      {
        limit: apl,
        color: 'grey',
        showTick: false,
        tooltip: { text: 'Out' }
      },
      {
        limit: Math.max(targetTiltAngle - 0.5*scale, -19.99),
        color: red10,
        showTick: false,
        tooltip: { text: 'AP Range' }
      },
      {
        limit: Math.min(targetTiltAngle + 0.5*scale, 19.99),
        color: tiltAngle <= tiltr && tiltAngle > apl ? red80 : red40,
        showTick: false,
        tooltip: { text: 'AP Range' }
      },
      {
        limit: apr,
        color: red10,
        showTick: false,
        tooltip: { text: 'AP Range' }
      },
      {
        limit: 90*scale,
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
          limit: rangel,
          color: 'grey',
          showTick: false,
          tooltip: { text: 'Out' }
        }]
        if(obRotationAngle && obRotationAngle < 0){
          array.push(
            {
              limit: Math.max(obRotationAngle - 0.5*scale, -49.99),
              color: blue10,
              showTick: false,
              tooltip: { text: 'OB Range' }
            },
            {
              limit: Math.min(obRotationAngle + 0.5*scale, apl - 0.01),
              color: (rotationAngle <= apl && rotationAngle > rangel) ? blue80 : blue40,
              showTick: false,
              tooltip: { text: 'OB Range' }
            },)
          array.push({
            limit: apl,
            color: blue10,
            showTick: false,
            tooltip: { text: 'OB Range' }
          },)
        }else if(obRotationAngle2 && obRotationAngle2 < 0){
          array.push(
            {
              limit: Math.max(obRotationAngle2 - 0.5*scale, -49.99),
              color: blue10,
              showTick: false,
              tooltip: { text: 'OB Range' }
            },
            {
              limit: Math.min(obRotationAngle2 + 0.5*scale, apl - 0.01),
              color: (rotationAngle <= apl && rotationAngle > rangel) ? blue80 : blue40,
              showTick: false,
              tooltip: { text: 'OB Range' }
            },)
          array.push({
            limit: apl,
            color: blue10,
            showTick: false,
            tooltip: { text: 'OB Range' }
          },)
        }else{
          array.push({
            limit: apl,
            color: (rotationAngle <= apl && rotationAngle > rangel) ? blue60 : blue10,
            showTick: false,
            tooltip: { text: 'OB Range' }
          },)}
        if(apRotationAngle){
          array.push(
            {
              limit: Math.max(apRotationAngle - 0.5*scale, apl + 0.01),
              color: red10,
              showTick: false,
              tooltip: { text: 'AP Range' }
            },
            {
              limit:Math.min(apRotationAngle + 0.5*scale, apr - 0.01),
              color: rotationAngle <= apr && rotationAngle > apl ? red80 : red40,
              showTick: false,
              tooltip: { text: 'AP Range' }
            },
          )
      
            array.push({
              limit: apr,
              color: red10,
              showTick: false,
              tooltip: { text: 'AP Range' }
            },)
        }else{
        array.push({
          limit: apr,
          color: rotationAngle <= apr && rotationAngle > apl ? red60 : red10,
          showTick: false,
          tooltip: { text: 'AP Range' }
        },)}
        if(obRotationAngle && obRotationAngle > 0){
          array.push(
            {
              limit: Math.max(obRotationAngle - 0.5*scale, apr),
              color: blue10,
              showTick: false,
              tooltip: { text: 'OB Range' }
            },
            {
              limit: Math.min(obRotationAngle + 0.5*scale, ranger - 0.01),
              color: (rotationAngle <= ranger && rotationAngle > apr) ? blue80 : blue40,
              showTick: false,
              tooltip: { text: 'OB Range' }
            },)
          array.push({
            limit: ranger,
            color: blue10,
            showTick: false,
            tooltip: { text: 'OB Range' }
          },)
        }else if(obRotationAngle2 && obRotationAngle2 > 0){
          array.push(
            {
              limit: Math.max(obRotationAngle2 - 0.5*scale, apr),
              color: blue10,
              showTick: false,
              tooltip: { text: 'OB Range' }
            },
            {
              limit: Math.min(obRotationAngle2 + 0.5*scale, ranger - 0.01),
              color: (rotationAngle <= ranger && rotationAngle > apr) ? blue80 : blue40,
              showTick: false,
              tooltip: { text: 'OB Range' }
            },)
          array.push({
            limit: ranger,
            color: blue10,
            showTick: false,
            tooltip: { text: 'OB Range' }
          },)
        }else{
          array.push({
            limit: ranger,
            color: (rotationAngle <= ranger && rotationAngle > apr) ? blue60 : blue10,
            showTick: false,
            tooltip: { text: 'OB Range' }
          })}
        
        array.push({
          limit: 90*scale,
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
          limit: rangel,
          color: 'grey',
          showTick: false,
          tooltip: { text: 'Out' }
        }]
        if (obRotationAngle < apl) {
          array.push({
            limit: apl,
            color: 'grey',
            showTick: false,
            tooltip: { text: 'OB Range' }
          },)
        }else{
          if(obRotationAngle2){
            array.push(
              {
                limit: Math.max(obRotationAngle2 - 0.5*scale, -49.99),
                color: blue10,
                showTick: false,
                tooltip: { text: 'OB Range' }
              },
              {
                limit: Math.min(obRotationAngle2 + 0.5*scale, apl - 0.01),
                color: (rotationAngle <= apl && rotationAngle > rangel) ? blue80 : blue40,
                showTick: false,
                tooltip: { text: 'OB Range' }
              },)
            array.push({
              limit: apl,
              color: blue10,
              showTick: false,
              tooltip: { text: 'OB Range' }
            },)
          }else{
            array.push({
              limit: apl,
              color: (rotationAngle <= apl && rotationAngle > rangel) ? blue60 : blue10,
              showTick: false,
              tooltip: { text: 'OB Range' }
            },)
          }        
        }
        array.push(
          {
            limit: Math.max(apRotationAngle - 0.5*scale, -19.99),
            color: red10,
            showTick: false,
            tooltip: { text: 'AP Range' }
          },
          {
            limit:Math.min(apRotationAngle + 0.5*scale, 19.99),
            color: rotationAngle <= apr && rotationAngle > apl ? red80 : red40,
            showTick: false,
            tooltip: { text: 'AP Range' }
          },
        )
        
        array.push({
          limit: apr,
          color: red10,
          showTick: false,
          tooltip: { text: 'AP Range' }
        },)
        if (obRotationAngle > apr) {
          array.push({
            limit: ranger,
            color: 'grey',
            showTick: false,
            tooltip: { text: 'OB Range' }
          },)
        }else{
          if(obRotationAngle2){
            array.push(
              {
                limit: Math.max(obRotationAngle2 - 0.5*scale, apr),
                color: blue10,
                showTick: false,
                tooltip: { text: 'OB Range' }
              },
              {
                limit: Math.min(obRotationAngle2 + 0.5*scale, ranger - 0.01),
                color: (rotationAngle <= ranger && rotationAngle > apr) ? blue80 : blue40,
                showTick: false,
                tooltip: { text: 'OB Range' }
              },)
            array.push({
              limit: ranger,
              color: blue10,
              showTick: false,
              tooltip: { text: 'OB Range' }
            },)
          }else{
          array.push({
            limit: ranger,
            color: (rotationAngle <= ranger && rotationAngle > apr) ? blue60 : blue10,
            showTick: false,
            tooltip: { text: 'OB Range' }
          },)
          }
        }
        array.push(
        {
          limit: 90*scale,
          color: 'grey',
          showTick: false,
          tooltip: { text: 'Out' }
        }
      )
    
      return array;
    }

    const array = [
      {
        limit: rangel,
        color: 'grey',
        showTick: false,
        tooltip: { text: 'Out' }
      }]
      
    if(isCupReg && usedOB > apr){
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
          limit: Math.max(obl - 0.5*scale, -49.99),
          color: blue10,
          showTick: false,
          tooltip: { text: 'OB Range' }
        },
        {
          limit: Math.min(obl + 0.5*scale, (obl + apRotationAngle)/2 - 0.01),
          color: (rotationAngle <= (obl + apRotationAngle)/2 && rotationAngle > rangel) ? blue80 : blue40,
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
        limit: Math.max(apRotationAngle - 0.5*scale, (obl + apRotationAngle)/2 + 0.01),
        color: red10,
        showTick: false,
        tooltip: { text: 'AP Range' }
      },
      {
        limit:Math.min(apRotationAngle + 0.5*scale, (apRotationAngle + obr)/2 - 0.01),
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

      if(isCupReg && usedOB <= apl){
        array.push({
          limit: ranger,
          color: 'grey',
          showTick: false,
          tooltip: { text: 'OB Range' }
        },)
      }else{
      array.push(
        {
          limit: Math.max(obr - 0.5*scale, (apRotationAngle + obr)/2 + 0.01),
          color: blue10,
          showTick: false,
          tooltip: { text: 'OB Range' }
        },
        {
          limit: Math.min(obr + 0.5*scale, 49.99),
          color: (rotationAngle <= ranger && rotationAngle > (apRotationAngle + obr)/2) ? blue80 : blue40,
          showTick: false,
          tooltip: { text: 'OB Range' }
        },
      )
    
      array.push({
        limit: ranger,
        color: blue10,
        showTick: false,
        tooltip: { text: 'OB Range' }
      },)}
      array.push({
        limit: 90*scale,
        color: 'grey',
        showTick: false,
        tooltip: { text: 'Out' }
      })
  
    return array;
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
          subArcs: getTiltArray(targetTiltAngle, tiltAngle)
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
        value={tiltAngle}
        minValue={-90*scale}
        maxValue={90*scale}
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
                if ((value <= apl && value >=rangel) || (value <= ranger && value > apr)) return 'Oblique';
                if (value <= apr && value >apl) return 'AP';
                return value;
              },
            },
            ticks: getRotaionTick(),
          }
        }}
        value={rotationAngle}
        minValue={-90*scale}
        maxValue={90*scale}
      />
      </>}


      <div className="hand" style={{ 
        transform: `rotate(${tiltAngle/scale}deg)`,
        position:'absolute', 
        top:'335px', 
        left:'263px', 
        zIndex:'11' 
      }}>
        <img src={require('./CarmTilt.png')} alt="indicator" />
      </div>
      <div className="hand" style={{ 
        transform: `rotate(${rotationAngle/scale}deg)`,
        position:'absolute', 
        top:'339px', 
        left:'1048px', 
        zIndex:'11' 
      }}>
        <img src={require('./CarmRotation.png')} alt="indicator" />
      </div>
      
      {/* Tilt tiltAngle display box */}
      <div style={{position:'absolute', alignItems:'center', top:'666px', left:'376px', zIndex:11}}>
        <img src={getBG(getTiltColor(), getDisplayTiltValue()[1])} alt="box" />
        <div style={{
          position:'absolute', 
          top: 0, 
          right:getDisplayTiltValue()[1] ? '113px' : '148px', 
          width:'100%', 
          textAlign:'right', 
          color: getTiltColor(),
          fontFamily:'abel', 
          fontSize:'75px'
        }}>
          {displayValue(getDisplayTiltValue()[0])[0]}
        </div>
        <div style={{
          position:'absolute', 
          top: 0, 
          left: getDisplayTiltValue()[1] ? '213px' : '179px', 
          width:'100%', 
          textAlign:'left', 
          color: getTiltColor(),
          fontFamily:'abel', 
          fontSize:'75px'
        }}>
          {displayValue(getDisplayTiltValue()[0])[1]}
        </div>

      </div>
      
      {/* Rotation tiltAngle display box */}
      <div style={{position:'absolute', top:'666px', left:'1157px', zIndex:11}}>
        <img src={getBG(getRotationColor(), getDisplayRotationValue()[1])} alt="box" />
        <div style={{
          position:'absolute', 
          top: 0, 
          right: getDisplayRotationValue()[1] ? '113px' : '148px', 
          width:'100%', 
          textAlign:'right', 
          color: getRotationColor(),
          fontFamily:'abel', 
          fontSize:'75px'
        }}>
          {displayValue(getDisplayRotationValue()[0])[0]}
        </div>
        <div style={{
          position:'absolute', 
          top: 0, 
          left: getDisplayRotationValue()[1] ? '213px' : '179px', 
          width:'100%', 
          textAlign:'left', 
          color: getRotationColor(),
          fontFamily:'abel', 
          fontSize:'75px'
        }}>
          {displayValue(getDisplayRotationValue()[0])[1]}
        </div>

      </div>
      {showIcon && 
      <img style={{position:'absolute', top:'652px', left:'862px', zIndex:11}} src={require('./CarmCheckmarks.png')} alt="box" />}
      
    </>
  );
}

export default L10;
