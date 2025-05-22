import React, { useState, useEffect, useRef } from 'react';

function L1({tracking, handlLabelClick}) {
    return(
        <>
        <img src={require('./NavBarBg.png')} style={{'position':'absolute', top:'962px', left:'0px'}}/>
        <img src={require('./ProgressBarBg.png')} style={{'position':'absolute', top:'971px', left:'281px'}}/>
        <img src={require('./NavMeasurementsBG.png')} style={{'position':'absolute', top:'977px', left:'667px'}}/>
        
        <img src={require('./Logo.png')} style={{'position':'absolute', top:'1041px', left:'13px'}}/>
        <img src={require('./PatientDataBg.png')} style={{'position':'absolute', top:'980px', left:'13px'}}/>
        <img src={require('./PatientIcon.png')} style={{'position':'absolute', top:'989px', left:'27px'}}/>

        {tracking?(<img src={require('./APLabel.png')} style={{'position':'absolute', top: '0px', left:'0px', zIndex:1}}/>):(
            <>
            <img src={require('./ManualAPLabelBg.png')} style={{'position':'absolute', top: '0px', left:'0px', zIndex:1}}/>
            <img className="image-button" src={require('./ManualAPLabel.png')} style={{'position':'absolute', top: '5px', left:'6px', zIndex:10}} onClick={()=>{handlLabelClick('ap')}}/>
            </>
        )}
        {tracking?(<img src={require('./OBLabel.png')} style={{'position':'absolute', top:'0px', left:'1787px', zIndex:1}}/>):(
            <>
            <img src={require('./ManualOBLabelBg.png')} style={{'position':'absolute', top: '0px', left:'1787px', zIndex:1}}/>
            <img className="image-button" src={require('./ManualOBLabel.png')} style={{'position':'absolute', top: '5px', left:'1793px', zIndex:10}} onClick={()=>{handlLabelClick('ob')}}/>
            </>
        )}

        </>
    )
}

export default L1;