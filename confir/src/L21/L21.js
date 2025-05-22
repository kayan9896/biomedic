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
  pelvis,
  setPelvis, 
  hasAp,
  hasOb,
  setLeftImageMetadata, 
  setRightImageMetadata, 
  editing,
  resetTemplate,
  setResetTemplate,
  setUseai
}) => {
  // State to track which template is selected (if any)
  const [selectedTemplate, setSelectedTemplate] = useState(resetTemplate ? pelvis[0] : null);

  // Handle template selection
  const handleTemplateClick = (template) => {
    setSelectedTemplate(template);
  };

  // Handle continue button click - load appropriate template and set pelvis
  const handleContinueClick = () => {
    if (selectedTemplate) {
      try {
        // Get the correct template data based on selection
        const templateData = selectedTemplate === 'l' 
          ? leftTemplateData 
          : rightTemplateData;
        
        // Set pelvis value based on selection
        
        if(selectedTemplate !== pelvis[0]){
          if(hasAp){
            setLeftImageMetadata(templateData);
            setPelvis((prev) => {
              let tmp = [...prev]
              tmp[0] = selectedTemplate
              return tmp
            })
          }
          if(hasOb){
            setRightImageMetadata(templateData);
            setPelvis((prev) => {
              let tmp = [...prev]
              tmp[1] = selectedTemplate
              return tmp
            })
          }
          setUseai([false, false])
        }else{
          if(editing === 'left') setLeftImageMetadata(templateData);
          if(editing === 'right') setRightImageMetadata(templateData);
        }
      } catch (error) {
        console.error('Error loading template:', error);
      }
      if(resetTemplate){
        setResetTemplate(false)
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
        src={selectedTemplate === 'l' ? LeftTemplateSelected : LeftTemplate} 
        alt="Left Template" 
        className="left-template" 
        style={{ 
          position: 'absolute', 
          left: selectedTemplate === 'l' ? '650px' : '655px', 
          top: selectedTemplate === 'l' ? '359px' : '364px',
          cursor: 'pointer' 
        }}
        onClick={() => handleTemplateClick('l')}
      />

      {/* Right Template */}
      <img 
        src={selectedTemplate === 'r' ? RightTemplateSelected : RightTemplate} 
        alt="Right Template" 
        className="right-template" 
        style={{ 
          position: 'absolute', 
          left: selectedTemplate === 'r' ? '993px' : '998px', 
          top: '364px',
          cursor: 'pointer' 
        }}
        onClick={() => handleTemplateClick('r')}
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