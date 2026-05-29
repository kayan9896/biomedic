import React, {useEffect, useState, useRef} from 'react';
import { Stage, Layer, Line, Circle, Image } from 'react-konva';

const Draft2 = ({handleNext, data, handlePoint, handleDrag}) => {

  const [i, setI] = useState(1)
  const [point, setPoint] = useState(null)
  const [active, setActive] = useState(null)

  useEffect(() => {
    setI(data.img_ap.length - 1)
    if(data.landmarks.point) setPoint(data.landmarks.point)
      console.log(data.landmarks)
  },[data])
  

  const [isMouseDown, setIsMouseDown] = useState(false);
  const [changeDown, setChangeDown] = useState(false);
  const [scale, setScale] = useState(1)
  const [topleft, setTopleft] = useState([0, 0]) 
  const lineRef = useRef(null);

  useEffect(() => {
    if(changeDown) handlePoint()
    
      const sc = (e) => {
        const rect = lineRef.current.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;

        const scrolled = e.deltaY * -0.001;
        console.log(scrolled, clientX, clientY, rect.left, rect.top)
        setScale((p) => {
          const nscale = Math.max(1, p + scrolled)
          setTopleft([clientX - (clientX - rect.left) * nscale / p - 190, clientY - (clientY - rect.top) * nscale / p - 49.25])
          return nscale;
        }) // Adjust the 0.001 to change sensitivity
        

      };
      document.getElementById('stitch')?.addEventListener('wheel', sc)
      return () => {
        document.getElementById('stitch')?.removeEventListener('wheel', sc)
      }
    })
  

  useEffect(() => {
      const handleGlobalMove = (e) => {
        if (!isMouseDown) return;
    
        const rect = lineRef.current.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        
        const x = (clientX - rect.left) / scale;
        const y = (clientY - rect.top) / scale;
        console.log(x,y,rect.x,rect.y)
        const newp = [...point]
        newp[active] = [x, y]
        setPoint(newp)
        handleDrag(newp);
    
      };
    
      const handleGlobalEnd = () => {
        setIsMouseDown(false);
      };
    
      window.addEventListener('mousemove', handleGlobalMove);
      window.addEventListener('mouseup', handleGlobalEnd);

    
      return () => {
        window.removeEventListener('mousemove', handleGlobalMove);
        window.removeEventListener('mouseup', handleGlobalEnd);}

    }, [isMouseDown]);

    const handleDotDown = (e, i) => {
    e.preventDefault()
    setIsMouseDown(true);
    setActive(i)
      
  };

  return (
    <>
      <img src={data.img_pelvis} style={{width: "30vh", height: "30vh", position:"absolute", right: '5vw', top: '5vh', border:'2px solid deepskyblue'}}/>
      <div style={{width: "30vh", height: "30vh", position:"absolute", right: '5vw', bottom: '15vh', border:'2px solid deepskyblue'}}>
        <img src={data.img_ap[i]} style={{width:'100%', height:'100%', display: data.img_ap[i] ? 'initial' : 'none'}}/>
        <button disabled={i === 0} style={{position:"absolute", left: '0%', bottom: '0%', width: '1vw'}} onClick={() => {setI(p => p - 1)}}>&lt;</button>
        <button disabled={i === data.img_ap.length - 1} style={{position:"absolute", right: '0%', bottom: '0%', width: '1vw'}} onClick={() => {setI(p => p + 1)}}>&gt;</button>

      </div>
      
      <div id = {'stitch'} style={{width: "60vw", height: "80vh", position:"absolute", right: '30vw', top: '5vh', border:'2px solid deepskyblue', overflow:'hidden'}}>
        <div ref={lineRef} style={{transform:`scale(${scale})`, transformOrigin:'0px 0px', left:`${topleft[0]}px`, top:`${topleft[1]}px`, position:'absolute'}}>
        <img src={data.img_stitch} style={{width:'100%', height:'100%', display: data.img_stitch ? 'initial' : 'none'}}/>
        {data.landmarks.lines?.map((p) => {
        return <svg 
          style={{ position: 'absolute', top: 0, left: 0, width:'100%', height:'100%' }}
          pointerEvents="none"
        >

          <path
            d={`M${p[0][0]},${p[0][1]}  L${p[1][0]},${p[1][1]}`}
            stroke={`teal`}
            strokeWidth={`${5 / scale}`}
            fill="none"
            pointerEvents="none"
          />
        </svg>})}
        {point && point.map((p, i) => <div
        
          className="draggable-dot"
          style={{
            width: `${20/scale}px`,
            height: `${20/scale}px`,
            backgroundColor: `red`,
            border: `${2/scale}px solid red`,
            borderRadius: '50%',
            position: 'absolute',
            cursor: 'move',
            left: `${p[0] - 12/scale}px`,
            top: `${p[1] - 12/scale}px`,
            touchAction: 'none',
            pointerEvents: "auto",
          }}
          onMouseDown={(e) => handleDotDown(e, i)}
        />)}
        </div>
        
        {/* <Stage ref={lineRef} width={window.innerWidth} height={window.innerHeight}>
          <Layer scaleX={scale} scaleY={scale}>
            
       
        {
          <Line
            points={[50, 50, 200, 50]}
            stroke={'teal'}
            strokeWidth={10}
            lineCap="round"
            lineJoin="round"
          />
        }

        
        {point?.map((p, i) => (
          <Circle
            x={p[0]}
            y={p[1]}
            radius={10}
            fill="red"
            onMouseDown={(e) => handleDotDown(e, i)}
          />
        ))}
      </Layer>
        </Stage> */}
      </div>
      

      <div style={{position:"relative", left: '40vw', top: '90vh', fontSize: '5vh', color:'white'}}>
        Measurement: {data.measure_anteversion}
      </div>
      <button disabled={!data.next_enable} style={{position:"relative", left: '70vw', top: '90vh', width: '5vw'}} onMouseDown={() => {setChangeDown(true)}} onMouseUp={() => {setChangeDown(false)}}>change</button>
      <button disabled={!data.next_enable} style={{position:"relative", left: '90vw', top: '90vh', width: '5vw'}} onClick={handleNext}>Next</button>

    </>
  );
};

export default Draft2;