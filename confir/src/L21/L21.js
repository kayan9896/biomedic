import React, { useState } from 'react';
import './L21.css';

// Import all the required images
import TemplateDialogueBoxBg from './SelectTemplateWindow.png';
import TemplateDialogueBtnDis from './TemplateDialogueBtnDis.png';
import TemplateDialogueBtn from '../L22/TemplateDialogueBtn.png';
import LeftTemplate from './LeftTemplate.png';
import RightTemplate from './RightTemplate.png';
import LeftTemplateSelected from '../L22/LeftTemplateSelected.png';
import RightTemplateSelected from '../L22/RightTemplateSelected.png';


const L21 = ({ 
  pelvis,
  setPelvis, 
  hasAp,
  hasOb,
  setLeftTmp, 
  setRightTmp, 
  editing,
  resetTemplate,
  setResetTemplate,
  setUseai,
  leftTemplateData,
  rightTemplateData,
  setResetWarning
}) => {
  // State to track which template is selected (if any)
  const [selectedTemplate, setSelectedTemplate] = useState(resetTemplate ? pelvis[0] : null);
  const [switchWarning, setSwitchWarning] = useState(false)

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
            setLeftTmp(templateData);
            setPelvis((prev) => {
              let tmp = [...prev]
              tmp[0] = selectedTemplate
              return tmp
            })
          }
          if(hasOb){
            setRightTmp(templateData);
            setPelvis((prev) => {
              let tmp = [...prev]
              tmp[1] = selectedTemplate
              return tmp
            })
          }
          setUseai([false, false])
        }else{
          if(editing === 'left') setLeftTmp(templateData);
          if(editing === 'right') setRightTmp(templateData);
        }
      } catch (error) {
        console.error('Error loading template:', error);
      }
      if(resetTemplate){
        setResetTemplate(false); 
        setResetWarning(false)
      }
    }
  };

  return (
    <div className="template-dialogue-container">
      <img src={require('../L10/BgBlur.png')} style={{position:'absolute', top:'0px', zIndex:21, aspectRatio:'1920/1080',height:'1080px'}}/>
      {/* Background */}
      <img 
        src={TemplateDialogueBoxBg} 
        alt="Dialog Background" 
        className="dialogue-bg" 
        style={{ position: 'absolute', left: '612px', top: '233px', zIndex: 21 }}
      />

      {/* Left Template */}
      <img 
        src={selectedTemplate === 'l' ? LeftTemplateSelected : LeftTemplate} 
        alt="Left Template" 
        className="left-template" 
        style={{ 
          position: 'absolute', 
          left: '669px', 
          top: '361px',
          cursor: 'pointer',
          zIndex: 21
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
          left: '985px', 
          top: '361px',
          cursor: 'pointer',
          zIndex: 21 
        }}
        onClick={() => handleTemplateClick('r')}
      />

      {/* Button (Enabled or Disabled based on selection) */}
      {selectedTemplate ? <img className="image-button" src={require('../L23/YesBtn.png')} style={{'position':'absolute', top:'663px', left:'761px', zIndex:21}} onClick={(resetTemplate && selectedTemplate !== pelvis[0] ? () => {setSwitchWarning(true)} : handleContinueClick)}/> :
      <img className="image-button" src={require('../L23/YesBtnDis.png')} style={{'position':'absolute', top:'663px', left:'761px', zIndex:21}}/>
      }
      <img className="image-button" src={require('../L23/NoBtn.png')} style={{'position':'absolute', top:'663px', left:'1035px', zIndex:21}} onClick={()=>{setResetTemplate(false)}}/>
        
      
      {switchWarning&&<>
          <img src={require('../L10/BgBlur.png')} style={{position:'absolute', top:'0px', zIndex:21, aspectRatio:'1920/1080',height:'1080px'}}/>
          <img src={require('../L21/SwitchTemplateSideWindow.png')} style={{'position':'absolute', top:'358px', left:'612px', zIndex:21}}/>
          <img className="image-button" src={require('../L23/YesBtn.png')} style={{'position':'absolute', top:'539px', left:'761px', zIndex:21}} onClick={()=>{handleContinueClick()}}/>
          <img className="image-button" src={require('../L23/NoBtn.png')} style={{'position':'absolute', top:'539px', left:'1035px', zIndex:21}} onClick={()=>{setResetTemplate(false)}}/>
        </>}
    </div>
  );
};

export default L21;