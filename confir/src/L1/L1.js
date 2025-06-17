import React, { useState, useEffect, useRef } from 'react';

function L1({tracking, handlLabelClick}) {
    return(
        <>
        <img src={require('./NavBarBg.png')} alt ="NavBarBg" style={{'position':'absolute', top:'962px', left:'0px'}}/>
        <img src={require('./ProgressBarBg.png')} alt ="ProgressBarBg" style={{'position':'absolute', top:'970px', left:'432px'}}/>
        <img src={require('./NavMeasurementsBG.png')} alt ="NavMeasurementsBG" style={{'position':'absolute', top:'970px', left:'960px'}}/>
        
        <img src={require('./Logo.png')} alt ="Logo" style={{'position':'absolute', top:'1041px', left:'13px', zIndex: 12}}/>
        <img src={require('./PatientDataBg.png')} alt ="PatientDataBg" style={{'position':'absolute', top:'980px', left:'13px', zIndex: 12}}/>
        <img src={require('./PatientIcon.png')} alt ="PatientIcon" style={{'position':'absolute', top:'989px', left:'27px', zIndex: 12}}/>

        {tracking?(<img src={require('./APLabel.png')} alt ="APLabel" style={{'position':'absolute', top: '0px', left:'0px', zIndex:1}}/>):(
            <>
            <img src={require('./ManualAPLabelBg.png')} alt ="ManualAPLabelBg" style={{'position':'absolute', top: '0px', left:'0px', zIndex:1}}/>
            <img className="image-button" alt ="ManualAPLabel" src={require('./ManualAPLabel.png')} style={{'position':'absolute', top: '5px', left:'6px', zIndex:10}} onClick={()=>{handlLabelClick('ap')}}/>
            </>
        )}
        {tracking?(<img src={require('./OBLabel.png')} alt ="OBLabel" style={{'position':'absolute', top:'0px', left:'1787px', zIndex:1}}/>):(
            <>
            <img src={require('./ManualOBLabelBg.png')} alt ="ManualOBLabelBg" style={{'position':'absolute', top: '0px', left:'1787px', zIndex:1}}/>
            <img className="image-button" alt ="ManualOBLabel" src={require('./ManualOBLabel.png')} style={{'position':'absolute', top: '5px', left:'1793px', zIndex:10}} onClick={()=>{handlLabelClick('ob')}}/>
            </>
        )}

        </>
    )
}

export default L1;