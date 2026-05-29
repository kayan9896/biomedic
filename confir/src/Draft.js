import React, {useEffect, useState} from 'react';


const Draft = ({handleNext, data}) => {

  const [z, setZ] = useState([1, 0, 1, 0])
  let mx = 1
  useEffect(() => {

    const p = 'img_left_1' in data ? 0 : 'img_left_2' in data ? 1 : 'img_right_1' in data ? 2 : 'img_right_2' in data ? 3 : null
    if(!p) return
    setZ((prev) => {
      const newz = [...prev]
      mx += 1
      z[p] = mx
      return z
    })
  },[data])

  return (
    <>
      <img src={data.img_left_1} style={{width: "20vh", height: "20vh", position:"absolute", right: '5vw', top: '5vh', border:'2px solid deepskyblue', zIndex:z[0]}}/>
      <img src={data.img_left_2} style={{width: "20vh", height: "20vh", position:"absolute", right: '15vw', top: '15vh', border:'2px solid deepskyblue', zIndex:z[1]}}/>

      <img src={data.img_right_1} style={{width: "20vh", height: "20vh", position:"absolute", right: '5vw', top: '55vh', border:'2px solid deepskyblue', zIndex:z[2]}}/>
      <img src={data.img_right_2} style={{width: "20vh", height: "20vh", position:"absolute", right: '15vw', top: '65vh', border:'2px solid deepskyblue', zIndex:z[3]}}/>

      <img src={data.img_stitch} style={{width: "60vw", height: "80vh", position:"absolute", right: '30vw', top: '5vh', border:'2px solid deepskyblue'}}/>

      <div style={{position:"relative", left: '40vw', top: '90vh', fontSize: '5vh', color:'white'}}>
        Measurement: {data.measure_lld}
      </div>

      <button disabled={!data.next_enable} style={{position:"relative", left: '90vw', top: '90vh', width: '5vw'}} onClick={handleNext}>Next</button>

    </>
  );
};

export default Draft;