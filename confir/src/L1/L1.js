import React, { useState, useEffect, useRef } from 'react';

function L1() {
    return(
        <>
        <img src={require('./NavBarBg.png')} style={{'position':'absolute', top:'962px', left:'0px'}}/>
        <img src={require('./ProgressBarBg.png')} style={{'position':'absolute', top:'971px', left:'281px'}}/>
        <img src={require('./NavMeasurementsBG.png')} style={{'position':'absolute', top:'977px', left:'667px'}}/>
        <img src={require('./AP label.png')} style={{'position':'absolute'}}/>
        <img src={require('./Logo.png')} style={{'position':'absolute', top:'1041px', left:'13px'}}/>
        <img src={require('./PatientDataBg.png')} style={{'position':'absolute', top:'980px', left:'13px'}}/>
        <img src={require('./PatientIcon.png')} style={{'position':'absolute', top:'989px', left:'27px'}}/>
        <img src={require('./OB label.png')} style={{'position':'absolute', top:'0px', left:'1787px'}}/>

        </>
    )
}

export default L1;