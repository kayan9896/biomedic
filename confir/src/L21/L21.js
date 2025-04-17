import React, { useState } from 'react';
import './L21.css';

// Import all the required images
import TemplateDialogueBoxBg from './TemplateDialogueBoxBg.png';
import TemplateDialogueBtnDis from './TemplateDialogueBtnDis.png';
import TemplateDialogueBtn from '../L22/TemplateDialogueBtn.png';
import LeftTemplate from './LeftTemplate.png';
import RightTemplate from './RightTemplate.png';
import LeftTemplateSelected from '../L22/LeftTemplateSelected.png';
import RightTemplateSelected from '../L22/RightTemplateSelected.png';

import leftTemplate from './template-l.json';
import rightTemplate from './template-r.json';
function scalePoints(templateData, scaleFactor) {
  const scaledData = JSON.parse(JSON.stringify(templateData)); // Create a deep copy of the data

  // Function to scale a single point
  const scalePoint = (point) => point.map(coord => coord * scaleFactor);
  console.log(Object.keys(scaledData))
  // Loop through the groups and scale points
  Object.keys(scaledData).forEach(groupKey => {
      scaledData[groupKey].forEach(item => {
          item.points = item.points.map(scalePoint); // Scale each point
      });
  });

  return scaledData;
}

const scaleFactor = 960 / 1024;
const leftTemplateData = scalePoints(leftTemplate, scaleFactor);
const rightTemplateData = scalePoints(rightTemplate, scaleFactor);

const L21 = ({ 
  setPelvis, 
  setLeftImageMetadata, 
  setRightImageMetadata, 
  activeLeft, 
  activeRight 
}) => {
  // State to track which template is selected (if any)
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  // Handle template selection
  const handleTemplateClick = (template) => {
    setSelectedTemplate(template);
  };

  // Handle continue button click - load appropriate template and set pelvis
  const handleContinueClick = () => {
    if (selectedTemplate) {
      try {
        // Get the correct template data based on selection
        const templateData = selectedTemplate === 'left' 
          ? leftTemplateData 
          : rightTemplateData;
        
        // Set pelvis value based on selection
        setPelvis(selectedTemplate === 'left' ? ['l', 'l'] : ['r', 'r']);
        
        // Update the appropriate image metadata based on which side is active
        if (activeLeft) {
          setLeftImageMetadata(templateData);
        } else if (activeRight) {
          setRightImageMetadata(templateData);
        }
      } catch (error) {
        console.error('Error loading template:', error);
      }
    }
  };

  return (
    <div className="template-dialogue-container">
      {/* Background */}
      <img 
        src={TemplateDialogueBoxBg} 
        alt="Dialog Background" 
        className="dialogue-bg" 
        style={{ position: 'absolute', left: '536px', top: '223px' }}
      />

      {/* Left Template */}
      <img 
        src={selectedTemplate === 'left' ? LeftTemplateSelected : LeftTemplate} 
        alt="Left Template" 
        className="left-template" 
        style={{ 
          position: 'absolute', 
          left: selectedTemplate === 'left' ? '650px' : '655px', 
          top: selectedTemplate === 'left' ? '359px' : '364px',
          cursor: 'pointer' 
        }}
        onClick={() => handleTemplateClick('left')}
      />

      {/* Right Template */}
      <img 
        src={selectedTemplate === 'right' ? RightTemplateSelected : RightTemplate} 
        alt="Right Template" 
        className="right-template" 
        style={{ 
          position: 'absolute', 
          left: selectedTemplate === 'right' ? '993px' : '998px', 
          top: '364px',
          cursor: 'pointer' 
        }}
        onClick={() => handleTemplateClick('right')}
      />

      {/* Button (Enabled or Disabled based on selection) */}
      <img 
        src={selectedTemplate ? TemplateDialogueBtn : TemplateDialogueBtnDis} 
        alt="Continue Button" 
        className="dialogue-btn" 
        style={{ 
          position: 'absolute', 
          left: '868px', 
          top: '656px',
          cursor: selectedTemplate ? 'pointer' : 'not-allowed'
        }}
        onClick={selectedTemplate ? handleContinueClick : undefined}
      />
    </div>
  );
};

export default L21;