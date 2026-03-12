(function() {
    const map = window.__map;
    if (!map) return;

    // Standard cartographic scales (1cm on map = value/100 cm in reality)
    const STANDARD_SCALES = [
        { label: '1:500',           value: 500,       cm1: '5 м' },
        { label: '1:1 000',         value: 1000,      cm1: '10 м' },
        { label: '1:2 000',         value: 2000,      cm1: '20 м' },
        { label: '1:5 000',         value: 5000,      cm1: '50 м' },
        { label: '1:10 000',        value: 10000,     cm1: '100 м' },
        { label: '1:20 000',        value: 20000,     cm1: '200 м' },
        { label: '1:25 000',        value: 25000,     cm1: '250 м' },
        { label: '1:50 000',        value: 50000,     cm1: '500 м' },
        { label: '1:100 000',       value: 100000,    cm1: '1 км' },
        { label: '1:150 000',       value: 150000,    cm1: '1,5 км' },
        { label: '1:200 000',       value: 200000,    cm1: '2 км' },
        { label: '1:300 000',       value: 300000,    cm1: '3 км' },
        { label: '1:500 000',       value: 500000,    cm1: '5 км' },
        { label: '1:750 000',       value: 750000,    cm1: '7,5 км' },
        { label: '1:1 000 000',     value: 1000000,   cm1: '10 км' },
        { label: '1:1 500 000',     value: 1500000,   cm1: '15 км' },
        { label: '1:2 000 000',     value: 2000000,   cm1: '20 км' },
        { label: '1:2 500 000',     value: 2500000,   cm1: '25 км' },
        { label: '1:3 000 000',     value: 3000000,   cm1: '30 км' },
        { label: '1:4 000 000',     value: 4000000,   cm1: '40 км' },
        { label: '1:5 000 000',     value: 5000000,   cm1: '50 км' },
        { label: '1:7 500 000',     value: 7500000,   cm1: '75 км' },
        { label: '1:10 000 000',    value: 10000000,  cm1: '100 км' },
        { label: '1:15 000 000',    value: 15000000,  cm1: '150 км' },
        { label: '1:20 000 000',    value: 20000000,  cm1: '200 км' },
        { label: '1:30 000 000',    value: 30000000,  cm1: '300 км' },
    ];

    // 96 DPI: 1px = 0.264mm, 1cm = ~38px
    var PX_PER_CM = 38;

    // Calculate real scale based on latitude and screen DPI
    function getRealScale() {
        var center = map.getCenter();
        var zoom = map.getZoom();
        // Meters per pixel at current latitude and zoom
        var metersPerPixel = 40075016.686 * Math.cos(center.lat * Math.PI / 180) / Math.pow(2, zoom + 8);
        // 96 DPI: 1px = 0.000264m
        return metersPerPixel / 0.000264;
    }

    // Find nearest standard scale
    function getNearestStandardScale(realScale) {
        var nearest = STANDARD_SCALES[0];
        var minDiff = Infinity;
        for (var i = 0; i < STANDARD_SCALES.length; i++) {
            var diff = Math.abs(Math.log(STANDARD_SCALES[i].value) - Math.log(realScale));
            if (diff < minDiff) {
                minDiff = diff;
                nearest = STANDARD_SCALES[i];
            }
        }
        return nearest;
    }

    // Find zoom for a given scale at current latitude
    function getZoomForScale(targetScale) {
        var center = map.getCenter();
        var cosLat = Math.cos(center.lat * Math.PI / 180);
        var zoom = Math.log2(40075016.686 * cosLat / (targetScale * 0.000264)) - 8;
        return Math.max(map.getMinZoom(), Math.min(map.getMaxZoom(), zoom));
    }

    // --- Scale control with ruler and dropdown ---
    var ScaleControl = L.Control.extend({
        options: { position: 'bottomright' },

        onAdd: function() {
            var container = L.DomUtil.create('div', 'scale-panel');
            L.DomEvent.disableClickPropagation(container);
            L.DomEvent.disableScrollPropagation(container);

            // Scale text
            this._scaleText = L.DomUtil.create('div', 'scale-text', container);

            // Ruler: fixed 1cm bar + label "1 см = X"
            this._rulerWrap = L.DomUtil.create('div', 'scale-ruler-wrap', container);
            this._rulerBar = L.DomUtil.create('div', 'scale-ruler-bar', this._rulerWrap);
            this._rulerBar.style.width = PX_PER_CM + 'px';
            this._rulerLabel = L.DomUtil.create('span', 'scale-ruler-label', this._rulerWrap);

            // Dropdown
            this._select = L.DomUtil.create('select', 'scale-select', container);
            for (var i = 0; i < STANDARD_SCALES.length; i++) {
                var opt = L.DomUtil.create('option', '', this._select);
                opt.value = STANDARD_SCALES[i].value;
                opt.textContent = STANDARD_SCALES[i].label;
            }

            this._select.addEventListener('change', function() {
                var targetScale = parseInt(this._select.value);
                var zoom = getZoomForScale(targetScale);
                map.setZoom(zoom);
            }.bind(this));

            this._update();
            return container;
        },

        _update: function() {
            var realScale = getRealScale();
            var nearest = getNearestStandardScale(realScale);

            this._scaleText.textContent = nearest.label;
            this._rulerLabel.textContent = '1 см = ' + nearest.cm1;
            this._select.value = nearest.value;
        }
    });

    var scaleControl = new ScaleControl();
    scaleControl.addTo(map);
    map.on('zoomend moveend', function() { scaleControl._update(); });
})();
