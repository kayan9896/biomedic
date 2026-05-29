import React, {useEffect, useState, useRef} from 'react';
import { Stage, Layer, Line, Circle, Image, Arrow } from 'react-konva';
import useImage from 'use-image';
import InteractiveCanvas from './InteractiveCanvas';

const Draft2 = ({handleNext, data, handlePoint, handleDrag}) => {

  const [i, setI] = useState(1)
  const [point, setPoint] = useState([[500,500]])
  const [active, setActive] = useState(null)
  const [imgurl, setImgurl] = useState(null)
  const [stitch] = useImage(imgurl)

  useEffect(() => {
    setI(data.img_ap.length - 1)
    if(data.landmarks.point) setPoint(data.landmarks.point)
    if(data.img_stitch) setImgurl(data.img_stitch)
  },[data])
  

  const isMouseDown = useRef(false);
  const [changeDown, setChangeDown] = useState(false);
  const [scale, setScale] = useState(1)
  const stageRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    if(changeDown) handlePoint()
    
      // const sc = (e) => {
      //   const cursor = stageRef.current.getPointerPosition();

      //   const scrolled = e.deltaY * -0.001;
  
      //   setScale((p) => {
      //     const nscale = Math.max(0.1, p + scrolled)
      //     console.log(nscale, cursor.x, stageRef.current.x())
      //     stageRef.current.position({x: cursor.x - (cursor.x - stageRef.current.x()) * nscale / p , y: cursor.y - (cursor.y - stageRef.current.y()) * nscale / p })
      //     return nscale;
      //   }) // Adjust the 0.001 to change sensitivity
        

      // };
      // document.getElementById('stitch')?.addEventListener('wheel', sc)
      // return () => {
      //   document.getElementById('stitch')?.removeEventListener('wheel', sc)
      // }
    })
  

  // useEffect(() => {
  //     const handleGlobalMove = (e) => {
  //       if (!isMouseDown.current) return;
        
  //       const cursor = stageRef.current.getPointerPosition();
        
  //       const x = (cursor.x - stageRef.current.x()) / scale;
  //       const y = (cursor.y - stageRef.current.y()) / scale;

  //       const newp = [...point]
  //       newp[active] = [x, y]
  //       setPoint(newp)
  //       handleDrag(newp);
    
  //     };
    
  //     const handleGlobalEnd = () => {
  //       isMouseDown.current = false
  //     };
    
  //     window.addEventListener('mousemove', handleGlobalMove);
  //     window.addEventListener('mouseup', handleGlobalEnd);
  //     window.addEventListener('touchmove', handleGlobalMove);
  //     window.addEventListener('touchend', handleGlobalEnd);

    
  //     return () => {
  //       window.removeEventListener('mousemove', handleGlobalMove);
  //       window.removeEventListener('mouseup', handleGlobalEnd);
  //       window.addEventListener('touchmove', handleGlobalMove);
  //       window.addEventListener('touchend', handleGlobalEnd);}

  //   }, [isMouseDown.current]);

  //   const handleDotDown = (e, i) => {
  //     isMouseDown.current = true
  //     setActive(i)
  //   };

    useEffect(() => {
      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/1.5.3/jspdf.debug.js';
      script.integrity = 'sha384-NaWTHo/8YCBYJ59830LTz/P4aQZK1sS0SneOgAvhsIl3zBu8r9RevNg5lHCHAuQ/';
      script.crossOrigin = 'anonymous';
      document.head.appendChild(script);
      
      return () => {
        document.head.removeChild(script);
      };
    }, []);

    const handleExport = () => {
    if (stageRef.current && typeof window.jsPDF !== 'undefined') {
      const stage = stageRef.current;
      const pdf = new window.jsPDF('l', 'px', [window.innerWidth, window.innerHeight]);
      pdf.setTextColor('#000000');
      
      // First add texts
      stage.find('Text').forEach((text) => {
        const size = text.fontSize() / 0.75; // convert pixels to points
        pdf.setFontSize(size);
        pdf.text(text.text(), text.x(), text.y(), {
          baseline: 'top',
          angle: -text.getAbsoluteRotation(),
        });
      });

      // Then put image on top of texts (so texts are not visible)
      pdf.addImage(
        stage.toDataURL({ pixelRatio: 2 }),
        0,
        0,
        window.innerWidth,
        window.innerHeight
      );

      pdf.save('canvas.pdf');
    } else {
      console.error('jsPDF library is not loaded or stage is not available');
      alert('jsPDF library is not loaded. In a real project, you need to include it.');
    }
  };

  // function getDistance(p1, p2) {
  //           return Math.sqrt(Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2));
  //       }

  // function getCenter(p1, p2) {
  //     return {
  //         x: (p1.x + p2.x) / 2,
  //         y: (p1.y + p2.y) / 2,
  //     };
  // }

  // let lastDist = 0
  // let lastCenter = null;
  // let lastpos = null
  // const touchzoom = (e) => {
  //   e.evt.preventDefault()
  //   let touch1 = e.evt.touches[0];
  //   let touch2 = e.evt.touches[1];

  //   if (touch1 && touch2) {
  //     var rect = containerRef.current.getBoundingClientRect();
  //     var p1 = {
  //         x: touch1.clientX - rect.left,
  //         y: touch1.clientY - rect.top,
  //     };
  //     var p2 = {
  //         x: touch2.clientX - rect.left,
  //         y: touch2.clientY - rect.top,
  //     };

  //     if (!lastCenter) {
  //         lastCenter = getCenter(p1, p2);
  //         return;
  //     }
  //     var newCenter = getCenter(p1, p2);
  //     var dist = getDistance(p1, p2);

  //     if (!lastDist) {
  //         lastDist = dist;
  //     }

  //     var pointTo = {
  //         x: (newCenter.x - stageRef.current.x()) / stageRef.current.scaleX(),
  //         y: (newCenter.y - stageRef.current.y()) / stageRef.current.scaleX(),
  //     };

  //     var scale = stageRef.current.scaleX() * (dist / lastDist);
  //     scale = Math.max(0.1, Math.min(scale, 10)); // bounds

  //     stageRef.current.scale({ x: scale, y: scale });

  //     var dx = newCenter.x - lastCenter.x;
  //     var dy = newCenter.y - lastCenter.y;

  //     var newPos = {
  //         x: newCenter.x - pointTo.x * scale + dx,
  //         y: newCenter.y - pointTo.y * scale + dy,
  //     };

  //     stageRef.current.position(newPos);
  //     lastDist = dist;
  //     lastCenter = newCenter
  //   }
  //   if (touch1 && !touch2){
  //       if(!lastpos){
  //           lastpos = [touch1.clientX, touch1.clientY]
  //       }else{
  //           let dx = touch1.clientX - lastpos[0]
  //           let dy = touch1.clientY - lastpos[1]
  //           lastpos = [touch1.clientX, touch1.clientY]
  //           stageRef.current.position({x: stageRef.current.x() + dx, y: stageRef.current.y() + dy})
  //       }
  //   }
  // };

  // const zoomend = () =>{
  //   lastDist = 0
  //   lastpos = null
  //   lastCenter = null
  // }

  const handlePointsChange = (update) => {
    setPoint(p => {
      update.forEach((item, idx) => {
        p[idx] = [item.x, item.y]
      })
      handleDrag(p)
      return p
    })
  }

  return (
    <>
      <img src={data.img_pelvis} style={{width: "30vh", height: "30vh", position:"absolute", right: '5vw', top: '5vh', border:'2px solid deepskyblue'}}/>
      <div style={{width: "30vh", height: "30vh", position:"absolute", right: '5vw', bottom: '15vh', border:'2px solid deepskyblue'}}>
        <img src={data.img_ap[i]} style={{width:'100%', height:'100%', display: data.img_ap[i] ? 'initial' : 'none'}}/>
        <button disabled={i === 0} style={{position:"absolute", left: '0%', bottom: '0%', width: '1vw'}} onClick={() => {setI(p => p - 1)}}>&lt;</button>
        <button disabled={i === data.img_ap.length - 1} style={{position:"absolute", right: '0%', bottom: '0%', width: '1vw'}} onClick={() => {setI(p => p + 1)}}>&gt;</button>

      </div>
      
      <div id = {'stitch'} ref={containerRef} style={{width: "60vw", height: "80vh", position:"absolute", right: '30vw', top: '5vh', border:'2px solid deepskyblue', overflow:'hidden'}}>
          <InteractiveCanvas
            ref={stageRef}
            image={data.img_stitch}
            initialPoints={point}
            lines={data.landmarks?.lines?.map(l => [l[0][0], l[0][1], l[1][0], l[1][1]])}
            onPointsChange={handlePointsChange}
            scale={scale}
            setScale={setScale}
          />
        {/* <Stage ref={stageRef} width={window.innerWidth} height={window.innerHeight} scaleX={scale} scaleY={scale} onTouchMove={touchzoom} onTouchEnd={zoomend}>
          <Layer>
            {<Image image={stitch}/>}
            {data.landmarks.lines?.map((l, i) => {
              const flatten = [l[0][0], l[0][1], l[1][0], l[1][1]]
              return <Line
                points={flatten}
                stroke={'teal'}
                strokeWidth={5 / scale}
              />})
              
            }
            {point?.map((p, i) => (
              <Circle
                x={p[0]}
                y={p[1]}
                radius={10 / scale}
                fill="red"
                onMouseDown={(e) => handleDotDown(e, i)}
                onTouchStart={(e) => handleDotDown(e, i)}
              />
            ))}
          </Layer>
        </Stage> */}
      </div>
      

      <div style={{position:"relative", left: '40vw', top: '90vh', fontSize: '5vh', color:'white'}}>
        Measurement: {data.measure_anteversion}
      </div>
      <button style={{position:"relative", left: '70vw', top: '90vh', width: '5vw'}} onMouseDown={() => {setChangeDown(true)}} onMouseUp={() => {setChangeDown(false)}}>change</button>
      <button style={{position:"relative", left: '80vw', top: '90vh', width: '5vw'}} onClick={handleExport}>Save</button>
      <button disabled={!data.next_enable} style={{position:"relative", left: '90vw', top: '90vh', width: '5vw'}} onClick={handleNext}>Next</button>

    </>
  );
};

export default Draft2;