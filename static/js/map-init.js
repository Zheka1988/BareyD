(function() {
    const map = L.map('map', { attributionControl: false, maxZoom: 20 }).setView([50.0, 30.0], 6);
    window.__map = map;

    // Online: L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18, maxNativeZoom: 18, attribution: '&copy; OpenStreetMap' }).addTo(map);
    L.tileLayer('/tiles/{z}/{x}/{y}.png', {
        maxZoom: 20,
        maxNativeZoom: 18,
        tms: true
    }).addTo(map);

    new L.Control.MiniMap(
        // Online: L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18 }),
        L.tileLayer('/tiles/{z}/{x}/{y}.png', { maxZoom: 18, tms: true }),
        { toggleDisplay: true, minimized: false, position: 'bottomleft', width: 150, height: 150, zoomLevelOffset: -5 }
    ).addTo(map);

    // Shared utilities
    window.__esc = function(str) {
        if (!str) return '';
        return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    };

    // Sidebar toggle
    const sidebar = document.getElementById('sidebar');
    document.getElementById('btn-collapse').addEventListener('click', () => {
        sidebar.classList.add('collapsed');
        setTimeout(() => map.invalidateSize(), 350);
    });
    document.getElementById('sidebar-toggle').addEventListener('click', () => {
        sidebar.classList.remove('collapsed');
        setTimeout(() => map.invalidateSize(), 350);
    });

    // Markers layer (shared)
    window.__markersLayer = L.markerClusterGroup({
        chunkedLoading: true,
        maxClusterRadius: 50,
        disableClusteringAtZoom: 18
    }).addTo(map);

    // Shared state
    window.__allObjects = [];
    window.__totalCount = 0;
    window.__hiddenIds = new Set();
    window.__hiddenObjects = {};
})();
