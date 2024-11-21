import React, { useRef, useEffect } from 'react';
import PointItem from './PointItem';
import { updateDistances } from './utils';

const ImageViewer = React.forwardRef(({ image, curves, updateCurves }, ref) => {
  const viewerRef = useRef(null);

  React.useImperativeHandle(ref, () => ({
    getViewerElement: () => viewerRef.current,
  }));

  useEffect(() => {
    if (image) {
      loadImage(image);
    }
  }, [image]);

  const loadImage = (imagePath) => {
    const viewer = viewerRef.current;
    viewer.innerHTML = '';
    viewer.style.backgroundImage = `url('${imagePath}')`;
    viewer.style.backgroundSize = 'contain';
    viewer.style.backgroundRepeat = 'no-repeat';
    viewer.style.backgroundPosition = 'center';
  };

  const handleUpdateDistances = () => {
    if (viewerRef.current) {
      updateDistances(curves, viewerRef.current);
    }
  };

  return (
    <div className="image-viewer-container">
      <div ref={viewerRef} className="image-viewer">
        {curves.map((curve, curveIndex) =>
          curve.map((point, pointIndex) => (
            <PointItem
              key={`${curveIndex}-${pointIndex}`}
              x={point.x}
              y={point.y}
              updateCurves={updateCurves}
              updateDistances={handleUpdateDistances}
            />
          ))
        )}
      </div>
    </div>
  );
});

export default ImageViewer;