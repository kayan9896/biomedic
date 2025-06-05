import React, { useState, useEffect, useRef } from 'react';
import Toggle from 'react-toggle';
import 'react-toggle/style.css';

function L14({setSetting, ai_mode, autocollect, tracking}) {
  // Data structure for placeholder texts
  const [items] = useState([
      { id: 1, text: 'AI Mode', isActive: ai_mode },
      { id: 2, text: 'Auto capture', isActive: autocollect },
      { id: 3, text: 'Tracking IMU', isActive: tracking },
      { id: 4, text: 'Placeholder 4', isActive: false },
      { id: 5, text: 'Placeholder 5', isActive: false },
      { id: 6, text: 'Placeholder 6', isActive: false },
      { id: 7, text: 'Placeholder 7', isActive: false },
      { id: 8, text: 'Placeholder 8', isActive: false },
      { id: 9, text: 'Placeholder 9', isActive: false },
      { id: 10, text: 'Placeholder 10', isActive: false },
      { id: 11, text: 'Placeholder 11', isActive: false },
  ]);

  const [toggleStates, setToggleStates] = useState(
      items.reduce((acc, item) => ({ ...acc, [item.id]: item.isActive }), {})
  );

  // Update toggle states when ai_mode prop changes
  useEffect(() => {
      setToggleStates(prev => ({
          ...prev,
          1: ai_mode
      }));
  }, [ai_mode]);

  const handleToggle = async (id) => {
      const newState = !toggleStates[id];
      
      // Update local state immediately for responsiveness
      setToggleStates(prev => ({
          ...prev,
          [id]: newState
      }));

      // If it's the AI Mode toggle, update the backend
      if (id === 1) {
          try {
              const response = await fetch('http://localhost:5000/api/setting', {
                  method: 'POST',
                  headers: {
                      'Content-Type': 'application/json',
                  },
                  body: JSON.stringify({ ai_mode: newState ? true : false }),
              });

              if (!response.ok) {
                  throw new Error('Failed to update AI mode');
              }
          } catch (error) {
              console.error('Error updating AI mode:', error);
              // Revert the toggle state if the update failed
              setToggleStates(prev => ({
                  ...prev,
                  [id]: !newState
              }));
          }
      }

      if (id === 2) {
        try {
            const response = await fetch('http://localhost:5000/api/setting', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ autocollect: newState ? true : false }),
            });

            if (!response.ok) {
                throw new Error('Failed to update AI mode');
            }
        } catch (error) {
            console.error('Error updating AI mode:', error);
            // Revert the toggle state if the update failed
            setToggleStates(prev => ({
                ...prev,
                [id]: !newState
            }));
        }
    }
    if (id === 3) {
        try {
            const response = await fetch('http://localhost:5000/api/setting', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ tracking: newState ? true : false }),
            });

            if (!response.ok) {
                throw new Error('Failed to update AI mode');
            }
        } catch (error) {
            console.error('Error updating AI mode:', error);
            // Revert the toggle state if the update failed
            setToggleStates(prev => ({
                ...prev,
                [id]: !newState
            }));
        }
    }
  };

  // Custom CSS for react-toggle color
  const toggleStyle = `
      .react-toggle--checked .react-toggle-track {
          background-color: #00B0F0 !important;
      }
      .react-toggle--checked:hover:not(.react-toggle--disabled) .react-toggle-track {
          background-color: #0096D1 !important;
      }
      .react-toggle--focus .react-toggle-thumb {
          box-shadow: 0 0 2px 3px #00B0F066;
      }
  `;

  return(
    <>
      <style>{toggleStyle}</style>
      <img src={require('../L10/BgBlur.png')} style={{position:'absolute', top:'0px', zIndex:13, aspectRatio:'1920/1080',height:'1080px'}}/>
      <img src={require('./SettingWindow.png')} alt="SettingWindow" style={{position:'absolute', top:'99px', left:'234px', zIndex:13}}/>
      <img src={require('./SettingExitBtn.png')} alt="SettingExit" style={{position:'absolute', top:'121px', left:'1617px', zIndex:13}} onClick={()=>setSetting(false)}/>
      <div style={{
          position: 'absolute',
          color: 'white',
          top: '222px',
          left: '305px',
          height: '222px',
          width: '1320px',
          zIndex: 13,
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gridTemplateRows: 'repeat(4, 1fr)',
          gap: '10px',
          padding: '10px',
          boxSizing: 'border-box',
      }}>
          {items.map(item => (
              <div key={item.id} style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '10px',
                  borderRadius: '4px',
                  backgroundColor: 'transparent',
              }}>
                  <span style={{ fontSize: '16px' }}>{item.text}</span>
                  <Toggle
                      checked={toggleStates[item.id]}
                      onChange={() => handleToggle(item.id)}
                      icons={false}
                  />
              </div>
          ))}
      </div>
    </>
  )
}

export default L14;