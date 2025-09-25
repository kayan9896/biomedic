function AdjustmentBar({ type, editing, value, onChange }) {
    const position = type === 'brightness' ? '270px' : '351px';
    const leftPosition = editing === 'left' ? 960 : 646;
    const middleValue = 100;
  
    const blueBarLeft = value < middleValue ? ((value - 0) / 100 * 87) : 87;
    const blueBarWidth = value < middleValue ? ((middleValue - value) / 100 * 87) : ((value - middleValue) / 100 * 87);
    
    return (
      <div
        style={{
          position: 'absolute',
          top: `calc(${position} - 0px)`,
          left: `${leftPosition}px`,
          width: '314px',
          height: '66px',
          backgroundColor: '#A0A3A3',
          borderRadius: '33px',
          border: '0px solid #555',
          zIndex: 7,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 35px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
          boxSizing: 'border-box',
        }}
      >
        {/* Minus sign container */}
        <div style={{ 
          width: '35px',
          height: '66px',  // Use full height
          position: 'relative',
        }}>
          <span style={{ 
            color: 'white', 
            fontSize: '32px',
            fontWeight: 'bold',
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-70%, -60%)',  // Perfect center
            lineHeight: 1,  // Prevent extra space above/below
          }}>−</span>
        </div>
        
        {/* Bar container */}
        <div style={{ 
          position: 'relative',
          width: '174px',
          height: '22px',
          display: 'flex', 
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          {/* Background grey bar */}
          <div
            style={{
              width: '100%',
              height: '22px',
              backgroundColor: '#fff',
              borderRadius: '11px',
              position: 'relative',
            }}
          >
            {/* Blue progress bar */}
            <div
              style={{
                position: 'absolute',
                top: '0',
                left: `${blueBarLeft}px`,
                width: `${blueBarWidth}px`,
                height: '100%',
                backgroundColor: '#00B0F0',
                borderRadius: '11px',
              }}
            />
          </div>
          
          {/* Range input */}
          <input
            type="range"
            min="0"
            max="200"
            value={value}
            onChange={(e) => onChange(parseFloat(e.target.value))}
            style={{
              position: 'absolute',
              width: '100%',
              height: '100%',
              top: '0',
              left: '0',
              WebkitAppearance: 'none',
              background: 'transparent',
              margin: '0',
              cursor: 'pointer',
              outline: 'none',
            }}
          />
        </div>
        
        {/* Plus sign container */}
        <div style={{ 
          width: '35px',
          height: '66px',  // Use full height
          position: 'relative',
        }}>
          <span style={{ 
            color: 'white', 
            fontSize: '32px',
            fontWeight: 'bold',
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-30%, -60%)',  // Perfect center
            lineHeight: 1,  // Prevent extra space above/below
          }}>+</span>
        </div>
      </div>
    );
  }
  
  export default AdjustmentBar;