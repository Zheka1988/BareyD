(function() {
    const map = window.__map;
    if (!map) return;

    const esc = window.__esc;
    const hiddenPanel = document.getElementById('hidden-panel');
    const hiddenList = document.getElementById('hidden-list');

    window._hideObject = function(id) {
        const obj = window.__allObjects.find(o => o.id === id);
        if (!obj) return;
        window.__hiddenIds.add(id);
        window.__hiddenObjects[id] = obj;
        map.closePopup();
        window.__renderMarkers();
        renderHiddenPanel();
    };

    window._showObject = function(id) {
        window.__hiddenIds.delete(id);
        delete window.__hiddenObjects[id];
        window.__renderMarkers();
        renderHiddenPanel();
    };

    function renderHiddenPanel() {
        if (window.__hiddenIds.size === 0) {
            hiddenPanel.style.display = 'none';
            return;
        }
        hiddenPanel.style.display = 'block';
        hiddenList.innerHTML = '';
        for (const id of window.__hiddenIds) {
            const obj = window.__hiddenObjects[id];
            const item = document.createElement('div');
            item.className = 'hidden-item';
            item.innerHTML = '<span class="hidden-item-name">' + esc(obj.name || 'Без названия') + '</span>' +
                '<button class="hidden-item-show" onclick="window._showObject(' + id + ')" title="Показать">&times;</button>';
            hiddenList.appendChild(item);
        }
    }

    document.getElementById('btn-show-all').addEventListener('click', () => {
        window.__hiddenIds.clear();
        Object.keys(window.__hiddenObjects).forEach(k => delete window.__hiddenObjects[k]);
        window.__renderMarkers();
        renderHiddenPanel();
    });
})();
