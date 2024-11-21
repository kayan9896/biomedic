import React from 'react';
import { Tabs, Tab, Box } from '@mui/material';

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index} style={{ width: '100%', height: '100%' }}>
      {value === index && <Box>{children}</Box>}
    </div>
  );
}

export default TabPanel;