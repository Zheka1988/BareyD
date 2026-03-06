(function() {
    const map = window.__map;
    if (!map) return;

    // ===== DRAWING =====
    const drawLayer = L.layerGroup().addTo(map);
    const drawnItems = [];
    let drawTool = null;
    let drawColor = '#ff4444';
    let drawWeight = 3;
    let drawFill = false;
    let drawStart = null;
    let drawPoints = [];
    let drawPreview = null;
    let selectedItem = null;

    const colorInput = document.getElementById('draw-color');
    const colorPreview = document.getElementById('draw-color-preview');
    const strokeInput = document.getElementById('draw-stroke');
    const fillBtn = document.getElementById('draw-fill');

    colorInput.addEventListener('input', (e) => {
        drawColor = e.target.value;
        colorPreview.style.background = drawColor;
    });
    colorPreview.style.background = drawColor;

    strokeInput.addEventListener('input', (e) => {
        drawWeight = parseInt(e.target.value);
    });

    fillBtn.addEventListener('click', () => {
        drawFill = !drawFill;
        fillBtn.classList.toggle('active', drawFill);
    });

    // Draw tool buttons
    const drawTools = ['pencil', 'line', 'circle', 'oval', 'rect', 'eraser'];
    drawTools.forEach(t => {
        document.getElementById('draw-' + t).addEventListener('click', () => {
            if (drawTool === t) {
                deactivateDrawTool();
                return;
            }
            activateDrawTool(t);
        });
    });

    document.getElementById('draw-clear-all').addEventListener('click', () => {
        drawLayer.clearLayers();
        drawnItems.length = 0;
        selectedItem = null;
    });

    function activateDrawTool(tool) {
        if (window.__deactivateMeasure) window.__deactivateMeasure();
        if (drawTool) document.getElementById('draw-' + drawTool).classList.remove('active');
        drawTool = tool;
        document.getElementById('draw-' + tool).classList.add('active');
        deselectItem();
        if (tool === 'eraser') {
            map.getContainer().style.cursor = 'pointer';
            map.dragging.enable();
        } else {
            map.getContainer().style.cursor = 'crosshair';
            map.dragging.disable();
        }
        map.doubleClickZoom.disable();
    }

    function deactivateDrawTool() {
        if (drawTool) document.getElementById('draw-' + drawTool).classList.remove('active');
        drawTool = null;
        isDrawing = false;
        drawPoints = [];
        drawStart = null;
        removePreview();
        map.getContainer().style.cursor = '';
        map.doubleClickZoom.enable();
        map.dragging.enable();
    }

    function removePreview() {
        if (drawPreview) {
            drawLayer.removeLayer(drawPreview);
            drawPreview = null;
        }
    }

    function getDrawStyle() {
        return {
            color: drawColor,
            weight: drawWeight,
            fillColor: drawColor,
            fillOpacity: drawFill ? 0.25 : 0,
            opacity: 1
        };
    }

    function addDrawnItem(layer) {
        layer.addTo(drawLayer);
        drawnItems.push(layer);
        layer.on('click', (e) => {
            L.DomEvent.stopPropagation(e);
            if (drawTool === 'eraser') {
                drawLayer.removeLayer(layer);
                const idx = drawnItems.indexOf(layer);
                if (idx > -1) drawnItems.splice(idx, 1);
                if (selectedItem === layer) selectedItem = null;
            } else if (!drawTool) {
                selectItem(layer);
            }
        });
    }

    function selectItem(layer) {
        deselectItem();
        selectedItem = layer;
        if (layer._path) layer._path.classList.add('drawing-selected');
    }

    function deselectItem() {
        if (selectedItem && selectedItem._path) {
            selectedItem._path.classList.remove('drawing-selected');
        }
        selectedItem = null;
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Delete' && selectedItem) {
            drawLayer.removeLayer(selectedItem);
            const idx = drawnItems.indexOf(selectedItem);
            if (idx > -1) drawnItems.splice(idx, 1);
            selectedItem = null;
        }
        if (e.key === 'Escape') {
            deactivateDrawTool();
        }
    });

    // --- Mouse handlers for drawing ---
    let isDrawing = false;

    map.on('mousedown', (e) => {
        if (!drawTool || drawTool === 'eraser') return;
        if (activeTool) return; // measurement active — skip drawing

        if (drawTool === 'pencil') {
            isDrawing = true;
            drawPoints = [e.latlng];
            drawPreview = L.polyline(drawPoints, getDrawStyle()).addTo(drawLayer);
        } else if (drawTool === 'line') {
            drawStart = e.latlng;
            isDrawing = true;
        } else if (['circle', 'oval', 'rect'].includes(drawTool)) {
            drawStart = e.latlng;
            isDrawing = true;
        }
    });

    map.on('mousemove', (e) => {
        if (!drawTool || drawTool === 'eraser') return;

        if (drawTool === 'pencil' && isDrawing && drawPreview) {
            drawPoints.push(e.latlng);
            drawPreview.setLatLngs(drawPoints);
        } else if (drawTool === 'line' && isDrawing && drawStart) {
            removePreview();
            drawPreview = L.polyline([drawStart, e.latlng], getDrawStyle()).addTo(drawLayer);
        } else if (drawTool === 'circle' && isDrawing && drawStart) {
            removePreview();
            const radius = drawStart.distanceTo(e.latlng);
            drawPreview = L.circle(drawStart, { ...getDrawStyle(), radius }).addTo(drawLayer);
        } else if (drawTool === 'oval' && isDrawing && drawStart) {
            removePreview();
            drawPreview = createOval(drawStart, e.latlng, getDrawStyle());
            drawPreview.addTo(drawLayer);
        } else if (drawTool === 'rect' && isDrawing && drawStart) {
            removePreview();
            const bounds = L.latLngBounds(drawStart, e.latlng);
            drawPreview = L.rectangle(bounds, getDrawStyle()).addTo(drawLayer);
        }
    });

    map.on('mouseup', (e) => {
        if (!drawTool || drawTool === 'eraser' || !isDrawing) return;

        if (drawTool === 'pencil') {
            isDrawing = false;
            if (drawPreview && drawPoints.length > 1) {
                drawLayer.removeLayer(drawPreview);
                addDrawnItem(L.polyline(drawPoints, getDrawStyle()));
            } else {
                removePreview();
            }
            drawPreview = null;
            drawPoints = [];
        } else if (drawTool === 'line' && drawStart) {
            isDrawing = false;
            if (drawPreview) {
                drawLayer.removeLayer(drawPreview);
            }
            addDrawnItem(L.polyline([drawStart, e.latlng], getDrawStyle()));
            drawPreview = null;
            drawStart = null;
        } else if (drawTool === 'circle' && drawStart) {
            isDrawing = false;
            if (drawPreview) {
                drawLayer.removeLayer(drawPreview);
            }
            const radius = drawStart.distanceTo(e.latlng);
            if (radius > 10) {
                addDrawnItem(L.circle(drawStart, { ...getDrawStyle(), radius }));
            }
            drawPreview = null;
            drawStart = null;
        } else if (drawTool === 'oval' && drawStart) {
            isDrawing = false;
            if (drawPreview) {
                drawLayer.removeLayer(drawPreview);
            }
            const latDiff = Math.abs(e.latlng.lat - drawStart.lat);
            const lngDiff = Math.abs(e.latlng.lng - drawStart.lng);
            if (latDiff > 0.0001 || lngDiff > 0.0001) {
                addDrawnItem(createOval(drawStart, e.latlng, getDrawStyle()));
            }
            drawPreview = null;
            drawStart = null;
        } else if (drawTool === 'rect' && drawStart) {
            isDrawing = false;
            if (drawPreview) {
                drawLayer.removeLayer(drawPreview);
            }
            const bounds = L.latLngBounds(drawStart, e.latlng);
            if (bounds.getNorth() !== bounds.getSouth()) {
                addDrawnItem(L.rectangle(bounds, getDrawStyle()));
            }
            drawPreview = null;
            drawStart = null;
        }
    });

    // Click on map to deselect drawn item
    map.on('click', (e) => {
        if (!drawTool && !activeTool && selectedItem) {
            deselectItem();
        }
    });

    function createOval(center, edgePoint, style) {
        const latDiff = Math.abs(edgePoint.lat - center.lat);
        const lngDiff = Math.abs(edgePoint.lng - center.lng);
        const points = [];
        const segments = 40;
        for (let i = 0; i < segments; i++) {
            const angle = (2 * Math.PI * i) / segments;
            points.push([
                center.lat + latDiff * Math.sin(angle),
                center.lng + lngDiff * Math.cos(angle)
            ]);
        }
        return L.polygon(points, style);
    }

    // ===== MEASUREMENT =====
    const toolResult = document.getElementById('tool-result');
    const coordsDisplay = document.getElementById('coords-display');
    let activeTool = null;
    let measurePoints = [];
    let measureLayers = L.layerGroup().addTo(map);

    function formatDistance(meters) {
        if (meters >= 1000) return (meters / 1000).toFixed(2) + ' km';
        return meters.toFixed(0) + ' m';
    }

    function formatArea(sqMeters) {
        if (sqMeters >= 1000000) return (sqMeters / 1000000).toFixed(2) + ' km2';
        return sqMeters.toFixed(0) + ' m2';
    }

    function calcPolygonArea(points) {
        if (points.length < 3) return 0;
        const latlngs = L.polygon(points).getLatLngs()[0];
        let area = 0;
        for (let i = 0; i < latlngs.length; i++) {
            const j = (i + 1) % latlngs.length;
            const p1 = L.Projection.SphericalMercator.project(latlngs[i]);
            const p2 = L.Projection.SphericalMercator.project(latlngs[j]);
            area += p1.x * p2.y - p2.x * p1.y;
        }
        return Math.abs(area) / 2;
    }

    function clearMeasure() {
        measurePoints = [];
        measureLayers.clearLayers();
        toolResult.style.display = 'none';
    }

    function finishMeasure() {
        if (measurePoints.length > 1) measurePoints.pop();
        map.getContainer().style.cursor = '';
        map.doubleClickZoom.enable();
        const hint = '<div class="result-hint" style="margin-top:6px;">' +
            '<a href="#" onclick="window._clearMeasure();return false;" style="color:#4a9eff;">Очистить</a></div>';
        if (activeTool === 'distance') {
            let total = 0;
            for (let i = 1; i < measurePoints.length; i++) {
                total += measurePoints[i - 1].distanceTo(measurePoints[i]);
            }
            toolResult.innerHTML = '<div class="result-label">Расстояние</div>' +
                '<div class="result-value">' + formatDistance(total) + '</div>' + hint;
        }
        if (activeTool === 'area') {
            const area = calcPolygonArea(measurePoints);
            toolResult.innerHTML = '<div class="result-label">Площадь</div>' +
                '<div class="result-value">' + formatArea(area) + '</div>' + hint;
        }
        activeTool = null;
        document.querySelectorAll('#measure-tools .tool-btn.active').forEach(b => {
            if (b.id !== 'tool-coords') b.classList.remove('active');
        });
    }

    window.__deactivateMeasure = function() {
        if (activeTool) {
            document.getElementById('tool-' + activeTool).classList.remove('active');
            clearMeasure();
            map.getContainer().style.cursor = '';
            map.doubleClickZoom.enable();
            activeTool = null;
        }
    };

    function setMeasureTool(tool) {
        deactivateDrawTool();

        if (activeTool === tool) {
            if (tool === 'area' && measurePoints.length >= 3) {
                finishMeasure();
                return;
            }
            activeTool = null;
            document.getElementById('tool-' + tool).classList.remove('active');
            clearMeasure();
            map.getContainer().style.cursor = '';
            map.doubleClickZoom.enable();
            return;
        }
        if (activeTool) {
            document.getElementById('tool-' + activeTool).classList.remove('active');
            clearMeasure();
        }
        activeTool = tool;
        document.getElementById('tool-' + tool).classList.add('active');
        map.getContainer().style.cursor = 'crosshair';
        map.doubleClickZoom.disable();
        map.dragging.enable();
        toolResult.style.display = 'block';
        const hint = tool === 'distance'
            ? 'Кликайте по карте. Двойной клик — завершить.'
            : 'Кликайте по карте. Нажмите кнопку ещё раз — завершить.';
        toolResult.innerHTML = '<div class="result-hint">' + hint + '</div>';
    }

    document.getElementById('tool-distance').addEventListener('click', () => setMeasureTool('distance'));
    document.getElementById('tool-area').addEventListener('click', () => setMeasureTool('area'));

    let coordsActive = false;
    document.getElementById('tool-coords').addEventListener('click', () => {
        coordsActive = !coordsActive;
        document.getElementById('tool-coords').classList.toggle('active', coordsActive);
        coordsDisplay.style.display = coordsActive ? 'block' : 'none';
        if (!coordsActive) coordsDisplay.textContent = '';
    });

    map.on('mousemove', (e) => {
        if (coordsActive) {
            coordsDisplay.textContent = e.latlng.lat.toFixed(5) + ', ' + e.latlng.lng.toFixed(5);
        }
    });

    // Measurement click — only when measurement tool is active and no draw tool
    map.on('click', (e) => {
        if (!activeTool || activeTool === 'coords') return;
        if (drawTool) return;

        measurePoints.push(e.latlng);
        L.circleMarker(e.latlng, { radius: 4, color: '#4a9eff', fillOpacity: 1 }).addTo(measureLayers);

        if (activeTool === 'distance') {
            if (measurePoints.length > 1) {
                const prev = measurePoints[measurePoints.length - 2];
                L.polyline([prev, e.latlng], { color: '#4a9eff', weight: 2, dashArray: '6,4' }).addTo(measureLayers);
            }
            let total = 0;
            for (let i = 1; i < measurePoints.length; i++) {
                total += measurePoints[i - 1].distanceTo(measurePoints[i]);
            }
            toolResult.innerHTML = '<div class="result-label">Расстояние</div>' +
                '<div class="result-value">' + formatDistance(total) + '</div>' +
                '<div class="result-hint">Двойной клик — завершить</div>' +
                '<div class="result-hint"><a href="#" onclick="window._clearMeasure();return false;" style="color:#4a9eff;">Очистить</a></div>';
        }

        if (activeTool === 'area') {
            measureLayers.eachLayer(l => { if (l instanceof L.Polygon) measureLayers.removeLayer(l); });
            if (measurePoints.length >= 3) {
                L.polygon(measurePoints, { color: '#4a9eff', weight: 2, fillOpacity: 0.15 }).addTo(measureLayers);
            } else if (measurePoints.length === 2) {
                L.polyline(measurePoints, { color: '#4a9eff', weight: 2, dashArray: '6,4' }).addTo(measureLayers);
            }
            const area = calcPolygonArea(measurePoints);
            toolResult.innerHTML = '<div class="result-label">Площадь</div>' +
                '<div class="result-value">' + (measurePoints.length >= 3 ? formatArea(area) : '...') + '</div>' +
                '<div class="result-hint"><a href="#" onclick="window._clearMeasure();return false;" style="color:#4a9eff;">Очистить</a></div>';
        }
    });

    map.on('dblclick', (e) => {
        if (!activeTool || activeTool === 'coords' || activeTool === 'area') return;
        if (drawTool) return;
        L.DomEvent.stop(e);
        finishMeasure();
    });

    window._clearMeasure = function() {
        clearMeasure();
    };
})();
