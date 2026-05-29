import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import 'react-simple-keyboard/build/css/index.css';

import L13 from './L13/L13';
import ReconnectionPage from './L13/ReconnectionPage';

import "@fontsource/abel"; // Defaults to weight 400
import "@fontsource/abel/400.css"; // Specify weight

import html2canvas from 'html2canvas';

import L24 from './L24/L24';

import Draft from './Draft';
import Draft2 from './Draft2';

import { io } from 'socket.io-client';
import Bar from './Bar';
import L17 from './L17/L17';
import UITest from './UITest';
import CircularProgress from './CircularProgress';
import L26 from './L26/L26';
const socket = io("http://206.12.6.202:5000");

function App() {

    const [setup, setSetup] = useState({
      'carm_model' : {},
      'carm_img' : null,
      'carm_status': false,
      'is_connected': false,
      'first_frame' : null,
      'selectedCArm': null,
      'currentStep': 1,
      'loading': false
    })

    const [preop, setPreop] = useState({
      'img_left_1' : null,
      'img_left_2' : null,
      'img_right_1' : null,
      'img_right_2' : null,
      'is_left_recon' : false,
      'is_right_recon' : false,
      'is_pelvis_recon' : false,
      'img_stitch' : null,
      'measure_lld' : null,
      'measure_offset' : null,
      'landmarks' : {},
      'next_enable': false
    })

    const [cup, setCup] = useState({
      'img_pelvis' : null,
      'img_ap' : [null],
      'img_stitch' : null,
      'measure_anteversion' : null,
      'measure_inclination' : null,
      'landmarks' : {},
      'next_enable' : false,
    })

    const [tri, setTri] = useState({
      'img_left_1' : null,
      'img_left_2' : null,
      'img_right_1' : null,
      'img_right_2' : null,
      'is_left_recon' : false,
      'is_right_recon' : false,
      'is_pelvis_recon' : false,
      'img_stitch' : null,
      'measure_lld' : null,
      'measure_offset' : null,
      'landmarks' : {},
      'next_enable': false
    })

    useEffect(() => {
      socket.on("connect", () => {
        console.log("Connected to server");
      });

      socket.on("setup", displaySetup);

      socket.on("preop", displayPreop);

      socket.on("cup", displayCup);

      socket.on("tri", displayTri);

      socket.on("error", (data) => {
        console.log(data);
        setError(data)
      });

      socket.on("percent", (data) => {
        setPercent(data)
      })

      socket.on("disconnect", () => {
        console.log("Disconnected from server");
      });

      return () => {
        socket.off("connect");
        socket.off("disconnect");
        socket.disconnect();
      };
    }, []);


  const [stage, setStage] = useState(0)

  const [error, setError] = useState(null);
  const [percent, setPercent] = useState(null)

  const displaySetup = (data) => {
    setStage(0)
    setSetup((prev) => {
      const newdict = {...prev}
      Object.keys(data).forEach((key) => {
        newdict[key] = data[key]
      })
      return newdict
    })
  }

  const displayPreop = (data) => {
    setStage(1)
    setPreop((prev) => {
      const newdict = {...prev}
      Object.keys(data).forEach((key) => {
        newdict[key] = data[key]
      })
      return newdict
    })
  }

  const displayCup = (data) => {
    setStage(2)
    setCup((prev) => {
      const newdict = {...prev}
      Object.keys(data).forEach((key) => {
        newdict[key] = data[key]
      })
      console.log(newdict)
      return newdict
    })
  }

  const displayTri = (data) => {
    setStage(3)
    setTri((prev) => {
      const newdict = {...prev}
      Object.keys(data).forEach((key) => {
        newdict[key] = data[key]
      })
      return newdict
    })
  }

  const handleNext = () => {
    setStage(p => p + 1)
  }
    
  const handleDl = async () => {}

  const handleCarm = (id, folder) => {
    socket.emit('carm', id, folder)
  }
  const checkVideo = () => {
    socket.emit('video')
  }
  const setSetupStep = (value) => {
    socket.emit('step', value)
  }
  const handlePoint = () => {
    socket.emit('landmark')
  }
  const handleDrag = (newp) => {
    socket.emit('drag', {'point': newp})
  }

  const [usb, setUsb] = useState(false)
  const [splash, setSplash] = useState(false)
  const [test, setTest] = useState(false)


  return (
    <div className="app">
      
      {stage === 0 ? (
        <div>
          {splash ? <L24 setSplash={setSplash}/> : 
          <L13 data={setup} setStage={setStage} setError={setError} fetchCarm={handleCarm} checkVideo={checkVideo} setcurrentStep={setSetupStep}/>
          }
        </div>) : 
        (<>
          {stage === 1 && <Draft handleNext={handleNext} data={preop}/>}
          {stage === 2 && <Draft2 handleNext={handleNext} data={cup} handlePoint={handlePoint} handleDrag={handleDrag}/>}
          {stage === 3 && <Draft handleNext={handleNext} data={tri}/>}
          {stage === 4 && <L17 handleDl={handleDl}/>}
        </>)
      
      } 

      <Bar stage={stage} setStage={setStage}/>
      {percent > 0 && percent < 100 && <CircularProgress percentage={percent}/>}
      {error && <L26 txt={error} setGe={setError} />}
      {test && <UITest displaySetup={displaySetup} displayPreop={displayPreop} displayCup={displayCup} displayTri={displayTri}/>}
    </div>)
}

export default App;

