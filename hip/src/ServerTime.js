import React, { useState, useEffect } from 'react';

function ServerTime() {
  const [serverTime, setServerTime] = useState('');

  useEffect(() => {
    const fetchServerTime = async () => {
      try {
        const response = await fetch('http://localhost:5000/time');
        const data = await response.json();
        setServerTime(data.time);
      } catch (error) {
        console.error('Error fetching server time:', error);
      }
    };

    // Initial fetch
    fetchServerTime();

    // Update every second
    const interval = setInterval(fetchServerTime, 1000);

    return () => clearInterval(interval);
  }, []);

  return <div className="server-time">{serverTime}</div>;
}

export default React.memo(ServerTime);