import React, { useEffect, useRef, useImperativeHandle, forwardRef } from 'react';
import Konva from 'konva';

const InteractiveCanvas = ({ image, initialPoints, lines, onPointsChange, scale, setScale }) => {
    const containerRef = useRef(null);
    const stageRef = useRef(null);

    useEffect(() => {
        if (!containerRef.current || !image) return;

        const container = containerRef.current;
        
        // Initialize Konva Stage with fallback dimensions to handle initial 0 size
        const initialWidth = container.width
        const initialHeight = container.height

        const stage = new Konva.Stage({
            container: container,
            width: initialWidth,
            height: initialHeight,
            scaleX: scale,
            scaleY: scale
        });
        stageRef.current = stage;

        const layer = new Konva.Layer();
        stage.add(layer);


        // Handle Resizing dynamically using ResizeObserver
        const resizeObserver = new ResizeObserver((entries) => {
            for (let entry of entries) {
                const { width: newWidth, height: newHeight } = entry.contentRect;
                if (newWidth === 0 || newHeight === 0) continue;

                // Check if stage was initialized with 0 size (or default fallback 800/600 but container actually had 0 size)
                const isInitialSetup = stage.width() === 800 && stage.height() === 600 && container.offsetWidth !== 800;

                const dx = stage.position().x - stage.width() / 2;
                const dy = stage.position().y - stage.height() / 2;

                stage.width(newWidth);
                stage.height(newHeight);

                stage.batchDraw();
            }
        });
        resizeObserver.observe(container);

        // Populate Map
        const allCircles = [];
        const konvaLines = [];

        // 1. Add lines synchronously
        if (lines) {
            lines.forEach(lineDef => {
                const line = new Konva.Line({
                    points: lineDef,
                    stroke: 'teal',
                    strokeWidth: 4,
                });
                layer.add(line);
                konvaLines.push({ line, def: lineDef });
            });
        }

        // 2. Add points synchronously
        if (initialPoints) {
            initialPoints.forEach(pointDef => {
                const circle = new Konva.Circle({
                    x: pointDef[0],
                    y: pointDef[1],
                    radius: 12,
                    fill: 'red',
                    stroke: 'white',
                    strokeWidth: 3,
                    draggable: true
                });

                // Record which lines have endpoints corresponding to this point
                const connectedLines = [];
                konvaLines.forEach(kl => {
                    const pts = kl.line.points();
                    for (let i = 0; i < pts.length; i += 2) {
                        if (pts[i] === pointDef[0] && pts[i + 1] === pointDef[1]) {
                            connectedLines.push({ line: kl.line, index: i });
                        }
                    }
                });

                //When dragging the circle, update the connected line coordinates
                circle.on('dragmove', () => {
                    const newX = circle.x();
                    const newY = circle.y();
                    connectedLines.forEach(cl => {
                        const pts = cl.line.points().slice();
                        pts[cl.index] = newX;
                        pts[cl.index + 1] = newY;
                        cl.line.points(pts);
                    });
                    layer.batchDraw();
                });

                // Bring point to top while dragging
                circle.on('dragstart', () => {
                    circle.moveToTop();
                });

                // Add interactivity for fun / feedback
                circle.on('mouseenter', () => {
                    document.body.style.cursor = 'pointer';
                    circle.strokeWidth(5);
                    layer.draw();
                });
                circle.on('mouseleave', () => {
                    document.body.style.cursor = 'default';
                    circle.strokeWidth(3);
                    layer.draw();
                });

                // Dragend callback to pass updated coordinates to the parent
                circle.on('dragend', () => {
                    if (onPointsChange) {
                        const updated = allCircles.map(c => ({
                            x: c.circle.x(),
                            y: c.circle.y(),
                        }));
                        onPointsChange(updated);
                    }
                });

                layer.add(circle);
                allCircles.push({circle });
            });
        }

        // Draw the layer with the synchronous shapes
        layer.batchDraw();

        // 3. Load image asynchronously
        const imgObj = new window.Image();
        imgObj.src = image;

        imgObj.onload = () => {
            

            const kImage = new Konva.Image({
                image: imgObj,
                x: 0,
                y: 0,
                width: window.innerWidth,
                height: window.innerHeight,
            });
            layer.add(kImage);
            kImage.moveToBottom();
            layer.batchDraw();
        };

        imgObj.onerror = (err) => {
            console.error("Failed to load background image:", image, err);
        };

        

        // Zooming functionality logic with constraints
        const scaleBy = 1.1;
        stage.on('wheel', (e) => {
            e.evt.preventDefault();

            const oldScale = stage.scaleX();
            const pointer = stage.getPointerPosition();
            if (!pointer) return;

            const mousePointTo = {
                x: (pointer.x - stage.x()) / oldScale,
                y: (pointer.y - stage.y()) / oldScale,
            };

            let newScale;
            if (e.evt.ctrlKey) {
                newScale = oldScale * Math.exp(-e.evt.deltaY * 0.01);
            } else {
                const direction = e.evt.deltaY > 0 ? -1 : 1;
                newScale = direction > 0 ? oldScale * scaleBy : oldScale / scaleBy;
            }

            newScale = Math.max(0.1, Math.min(newScale, 10)); // bounds

            stage.scale({ x: newScale, y: newScale });

            const newPos = {
                x: pointer.x - mousePointTo.x * newScale,
                y: pointer.y - mousePointTo.y * newScale,
            };

            stage.position(newPos);
            setScale(newScale)
            stage.batchDraw();
        });

        // Disable single touch panning on the stage
        stage.on('dragstart', (e) => {
            if (e.target === stage) {
                const isTouch = e.evt && (e.evt.type.includes('touch') || e.evt.pointerType === 'touch');
                if (isTouch) {
                    stage.stopDrag();
                }
            }
        });

        // Pinch-to-zoom functionality helpers
        function getDistance(p1, p2) {
            return Math.sqrt(Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2));
        }

        function getCenter(p1, p2) {
            return {
                x: (p1.x + p2.x) / 2,
                y: (p1.y + p2.y) / 2,
            };
        }

        let lastCenter = null;
        let lastDist = 0;
        let lastpos = null

        stage.on('touchmove', function (e) {
            e.evt.preventDefault()
            var touch1 = e.evt.touches[0];
            var touch2 = e.evt.touches[1];

            if (touch1 && touch2) {
                if (stage.isDragging()) {
                    stage.stopDrag();
                }

                var rect = container.getBoundingClientRect();
                var p1 = {
                    x: touch1.clientX - rect.left,
                    y: touch1.clientY - rect.top,
                };
                var p2 = {
                    x: touch2.clientX - rect.left,
                    y: touch2.clientY - rect.top,
                };

                if (!lastCenter) {
                    lastCenter = getCenter(p1, p2);
                    return;
                }
                var newCenter = getCenter(p1, p2);
                var dist = getDistance(p1, p2);

                if (!lastDist) {
                    lastDist = dist;
                }

                var pointTo = {
                    x: (newCenter.x - stage.x()) / stage.scaleX(),
                    y: (newCenter.y - stage.y()) / stage.scaleX(),
                };

                var scale = stage.scaleX() * (dist / lastDist);
                scale = Math.max(0.1, Math.min(scale, 10)); // bounds

                stage.scale({ x: scale, y: scale });
                setScale(newPos.x)

                var dx = newCenter.x - lastCenter.x;
                var dy = newCenter.y - lastCenter.y;

                var newPos = {
                    x: newCenter.x - pointTo.x * scale + dx,
                    y: newCenter.y - pointTo.y * scale + dy,
                };

                stage.position(newPos);
                stage.batchDraw();

                lastDist = dist;
                lastCenter = newCenter;
            }

            if (touch1 && !touch2){
                if(!lastpos){
                    lastpos = [touch1.clientX, touch1.clientY]
                }else{
                    dx = touch1.clientX - lastpos[0]
                    dy = touch1.clientY - lastpos[1]
                    lastpos = [touch1.clientX, touch1.clientY]
                    stage.position({x: stage.x() + dx, y: stage.y() + dy})
                }
            }
        });

        stage.on('touchend', function () {
            lastDist = 0;
            lastCenter = null;
            lastpos = null
        });

        // Cleanup
        return () => {
            resizeObserver.disconnect();
            stage.destroy();
            document.body.style.cursor = 'default';
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [image, initialPoints, lines, scale]);

    return (
        <div ref={containerRef} id="container" style={{width: '100%', height: '100%'}}/>
    );
};

InteractiveCanvas.displayName = 'InteractiveCanvas';

export default InteractiveCanvas;
