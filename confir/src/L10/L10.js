import React from 'react';
import GaugeComponent from 'react-gauge-component';

function L10({angle, rotationAngle, isTiltSaved, isRotationSaved}) {
  return(
    <>
      <img src={require('./BgBlur.png')} alt="ReportImageViewport" style={{position:'absolute', zIndex:10}}/>
      <div style={{position:'absolute', top:'74px', left:'217px', zIndex:10}}>
        <img src={require('./C-armAgnleAdjustmentWindowBg.png')} alt="box" />
      </div>
      <div style={{position:'absolute',top:'600px',left:'1040'}}>+</div>
      <GaugeComponent
        type="semicircle"
        style={{position:'absolute',top:'0px', width:'774px',transform:'translate(223px,252px)',zIndex:10}}
        marginInPercent={{left: 0, right: 0, top: 0.18, bottom: 0}}
        arc={{
          width: 0.2,
          padding: 0,
          cornerRadius: 1,
          subArcs: [
            {
              limit: -20, // -22.5 degrees
              color: 'grey',
              showTick: false,
              tooltip: { text: 'Out' }
            },
            {
              limit: 20, // 14.5 degrees
              color: (angle <= 20 && angle >-20) ? '#ffa471' : '#EFDACD',
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
        }}
        pointer={{
          color: '#ffffff',
          length: 0.1,
          width: 15,
          elastic: false,
          type:'arrow',
          hide:true
        }}
        labels={{
          valueLabel: { hide:true, formatTextValue: value => value + '°' },
          tickLabels: {
            type: 'outer',
            hideMinMax: true,
            defaultTickValueConfig: {
              formatTextValue: (value) => {
                if ((value <= -20 && value >=-50) || (value <= 50 && value >20)) return 'Oblique';
                if (value <= 20 && value >-20) return 'AP';
                return value + '°';
              },
            }
          }
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
          subArcs: [
            {
              limit: -50,
              color: 'grey',
              showTick: false,
              tooltip: { text: 'Out' }
            },
            {
              limit: -20,
              color: (rotationAngle <= -20 && rotationAngle >=-50) ? '#3ca4e5' : '#C3D3E0',
              showTick: false,
              tooltip: { text: 'OB Range' }
            },
            {
              limit: 20,
              color: (rotationAngle <= 20 && rotationAngle >-20) ? '#ffa471' : '#EFDACD',
              showTick: false,
              tooltip: { text: 'AP Range' }
            },
            {
              limit: 50,
              color: (rotationAngle <= 50 && rotationAngle >20) ? '#3ca4e5' : '#C3D3E0',
              showTick: false,
              tooltip: { text: 'OB Range' }
            },
            {
              limit: 90,
              color: 'grey',
              showTick: false,
              tooltip: { text: 'Out' }
            }
          ]
        }}
        pointer={{
          color: '#ffffff',
          length: 0.1,
          width: 15,
          elastic: false,
          type:'arrow',
          hide:true
        }}
        labels={{
          valueLabel: { hide:true, formatTextValue: value => value + '°' },
          tickLabels: {
            type: 'outer',
            hideMinMax: true,
            defaultTickValueConfig: {
              formatTextValue: (value) => {
                if ((value <= -20 && value >=-50) || (value <= 50 && value >20)) return 'Oblique';
                if (value <= 20 && value >-20) return 'AP';
                return value + '°';
              },
            },
            ticks: [
              {
                value: -35,
                valueConfig:{
                  style: {
                  fontSize: (rotationAngle <= -20 && rotationAngle >=-50)? '50px' : '30px',
                  fill:'white',
                  fontFamily:'abel'
                }},
                lineConfig:{width:(rotationAngle <= -20 && rotationAngle >=-50)? '5px' : '3px',
                  length:(rotationAngle <= -20 && rotationAngle >=-50)? 15 : 5,
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
                  length:(rotationAngle <= 20 && rotationAngle >-20)? 15 : 5,
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
                  length:(rotationAngle <= 50 && rotationAngle >20) ? 15 : 5,
                  distanceFromArc: (rotationAngle <= 50 && rotationAngle >20) ? 3 : 5,color:'#ffffff'}
              }
            ],
          }
        }}
        value={rotationAngle}
        minValue={-90}
        maxValue={90}
      />
      <div className="hand" style={{ 
        transform: `rotate(${angle}deg)`,
        position:'absolute', 
        top:'337px', 
        left:'343px', 
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
      <div style={{position:'absolute', alignItems:'center', top:'666px', left:'496px', zIndex:11}}>
        <img src={require('./APAngleDegreeBg.png')} alt="box" />
        <div style={{
          position:'absolute', 
          top: 0, 
          left:0, 
          width:'100%', 
          textAlign:'center', 
          color: angle >= -20 && angle <= 20 ? '#CD5445' : '#FF0000',
          fontFamily:'abel', 
          fontSize:'80px'
        }}>
          {isTiltSaved ? 'saved' : `${angle}°`}
        </div>
        {!(angle >= -20 && angle <= 20) && (
          <div style={{
            position:'absolute', 
            top: '85px', 
            left:0, 
            width:'100%', 
            textAlign:'center', 
            color:'#FF0000', 
            fontFamily:'abel', 
            fontSize:'20px'
          }}>
            Out of range
          </div>
        )}
      </div>
      <div style={{position:'absolute', top:'666px', left:'1199px', zIndex:11}}>
        <img src={require('./OBAngleDegreeBg.png')} alt="box" />
        <div style={{
          position:'absolute', 
          top: 0, 
          left:0, 
          width:'100%', 
          textAlign:'center', 
          color: (!(rotationAngle >= -15 && rotationAngle <= 15) || (rotationAngle >= -20 && rotationAngle <= 20)) ? '#0260A0' : '#FF0000',
          fontFamily:'abel', 
          fontSize:'80px'
        }}>
          {isRotationSaved ? 'saved' : `${rotationAngle}°`}
        </div>
        {(rotationAngle >= -15 && rotationAngle <= 15) && !(rotationAngle >= -20 && rotationAngle <= 20) && (
          <div style={{
            position:'absolute', 
            top: '85px', 
            left:0, 
            width:'100%', 
            textAlign:'center', 
            color:'#FF0000', 
            fontFamily:'abel', 
            fontSize:'20px'
          }}>
            Out of range in AP mode
          </div>
        )}
      </div>
    </>
  )
}

export default L10;