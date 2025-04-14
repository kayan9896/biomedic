import React, { useState, useEffect } from 'react';

function L13({ handleConnect }) {
  const [cArms, setCArms] = useState([]);
  const [selectedCArm, setSelectedCArm] = useState('');
  const [cArmSelected, setCarmSelected] = useState(false);
  const [videoConnected, setVideoConnected] = useState(false);
  const [error, setError] = useState(null);

  // Fetch C-arm data when component mounts
  useEffect(() => {
    const fetchCArms = async () => {
      try {
        const response = await fetch('http://localhost:5000/get-carms');
        if (!response.ok) {
          throw new Error('Failed to fetch C-arm data');
        }
        const data = await response.json();
        setCArms(data);
      } catch (err) {
        setError('Error loading C-arm data: ' + err.message);
        console.error(err);
      }
    };

    fetchCArms();
  }, []);

  const handleCarmChange = (e) => {
    setSelectedCArm(e.target.value);
    setCarmSelected(e.target.value !== '');
  };

  const checkVideoConnection = async () => {
    try {
      const response = await fetch('http://localhost:5000/check-video-connection');
      if (!response.ok) {
        throw new Error('Failed to check video connection');
      }
      const data = await response.json();
      setVideoConnected(data.connected);
    } catch (err) {
      setError('Error checking video connection: ' + err.message);
      console.error(err);
    }
  };

  // Attempt to auto-detect video connection when C-arm is selected
  useEffect(() => {
    if (cArmSelected) {
      checkVideoConnection();
    }
  }, [cArmSelected]);

  const getSelectedCArmImage = () => {
    if (!selectedCArm || !cArms[selectedCArm]) return null;
    
    return (
      <img 
        src={cArms[selectedCArm].image} // Direct URL from backend
        alt={`${selectedCArm} preview`} 
        style={{
          position: 'absolute', 
          zIndex: 14, 
          top: '140px', 
          left: '1025px',
          maxWidth: '500px',
          maxHeight: '400px'
        }}
      />
    );
  };

  return (
    <div>
      <img src={require('./SetupWindow.png')} alt="SetupWindow" style={{position:'absolute', top:'6px', left:'240px', zIndex:13}}/>
      <img src={require('./SetupTryAgain.png')} alt="SetupTryAgain" style={{position:'absolute', top:'826px', left:'995px', zIndex:13, cursor: videoConnected ? 'default' : 'pointer'}} 
        onClick={videoConnected ? null : checkVideoConnection} />
      <img src={require('./SetupReturn.png')} alt="SetupReturn" style={{position:'absolute', top:'826px', left:'1330px', zIndex:13, cursor: (cArmSelected && videoConnected) ? 'pointer' : 'default'}} 
        onClick={(cArmSelected && videoConnected) ? handleConnect : null} />
      <img src={require('../L1/Logo.png')} style={{position:'absolute', top:'1041px', left:'13px'}} />
      <img src={require('../L2/ExitIcon.png')} style={{position:'absolute', top:'1016px', left:'1853px'}} />

      <img src={require(cArmSelected ? './CrossWhite.png' : './CrossGray.png')} 
        style={{position:'absolute', zIndex:13, top:'153px', left:'329px'}} />
      <div style={{position:'absolute', fontFamily:'abel', fontSize:'46px', color: '#00B0F0', width: '538px', zIndex:13, top:'148px', left:'385px'}}>C-ARM EQUIPMENT</div>
      
      <select 
        value={selectedCArm}
        onChange={handleCarmChange}
        style={{position:'absolute', fontFamily:'abel', zIndex:13, width: '546px', height:'58px', top:'224px', left:'329px'}}>
          <option value="">Select a C-arm model</option>
          {Object.keys(cArms).map(carmName => (
            <option key={carmName} value={carmName}>{carmName}</option>
          ))}
      </select>
      
      <div style={{position:'absolute', fontFamily:'abel', fontSize:'30px', color: cArmSelected ? '#FFFFFF' : '#686868', width: '498px', zIndex:13, top:'289px', left:'385px'}}>
        {cArmSelected ? 'C-arm has been successfully selected.' : 'Please select the C-arm model.'}
      </div>

      <img src={require(videoConnected ? './CrossWhite.png' : './CrossGray.png')} 
        style={{position:'absolute', zIndex:13, top:'364px', left:'329px'}} />
      <div style={{position:'absolute', fontFamily:'abel', fontSize:'46px', color: '#00B0F0', width: '538px', zIndex:13, top:'358px', left:'385px'}}>VIDEO CONNECTION</div>
      
      <div style={{position:'absolute', fontFamily:'abel', fontSize:'30px', color: videoConnected ? '#FFFFFF' : '#686868', width: '498px', zIndex:13, top:'435px', left:'385px'}}>
        {videoConnected ? 'Video input detected successfully.' : 'Video input not detected.'}
      </div>

      <img src={require('./C-armEquipmentInstruction.png')} style={{position:'absolute', zIndex:13, top:'134px', left:'1015px'}} />
      
      {/* Display selected C-arm image */}
      {cArmSelected && getSelectedCArmImage()}
      
      {/* Error message if needed */}
      {error && (
        <div style={{position:'absolute', fontFamily:'abel', fontSize:'24px', color: 'red', zIndex:15, top:'500px', left:'385px', maxWidth: '500px'}}>
          {error}
        </div>
      )}
    </div>
  );
}

export default L13;