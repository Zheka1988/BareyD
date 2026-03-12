(function() {
    const FILTERS_URL = window.__FILTERS_URL;
    const MARKERS_URL = window.__MARKERS_URL;
    const SEARCH_URL = window.__SEARCH_URL;
    const LOG_EXPORT_URL = window.__LOG_EXPORT_URL;

    function esc(str) {
        if (!str) return '';
        return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    // --- Map ---
    const map = L.map('map').setView([50.0, 30.0], 6);
    window.__map = map;
    // Online: L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18, attribution: '&copy; OpenStreetMap' }).addTo(map);
    L.tileLayer('/tiles/{z}/{x}/{y}.png', {
        maxZoom: 18,
        tms: true,
        attribution: '&copy; OpenStreetMap'
    }).addTo(map);

    new L.Control.MiniMap(
        // Online: L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18 }),
        L.tileLayer('/tiles/{z}/{x}/{y}.png', { maxZoom: 18, tms: true }),
        { toggleDisplay: true, minimized: false, position: 'bottomleft', width: 150, height: 150, zoomLevelOffset: -5 }
    ).addTo(map);

    const markersLayer = L.markerClusterGroup({
        chunkedLoading: true,
        maxClusterRadius: 50,
        disableClusteringAtZoom: 18
    }).addTo(map);
    let allObjects = [];
    let totalCount = 0;
    const hiddenIds = new Set();
    const hiddenObjects = {};
    let fetchController = null;

    // --- Sidebar toggle ---
    const sidebar = document.getElementById('sidebar');
    document.getElementById('btn-collapse').addEventListener('click', () => {
        sidebar.classList.add('collapsed');
        setTimeout(() => map.invalidateSize(), 350);
    });
    document.getElementById('sidebar-toggle').addEventListener('click', () => {
        sidebar.classList.remove('collapsed');
        setTimeout(() => map.invalidateSize(), 350);
    });

    // --- Filters ---
    const filterKeys = ['country', 'gov_org', 'type', 'kind', 'association', 'unit'];
    const dependentKeys = ['gov_org', 'type', 'kind', 'association', 'unit'];
    const filterSections = {};
    const filterSelected = {};

    filterKeys.forEach(k => {
        filterSelected[k] = new Set();
        const section = document.querySelector('.filter-section[data-filter="' + k + '"]');
        filterSections[k] = section;

        section.querySelector('.filter-header').addEventListener('click', (e) => {
            if (e.target.closest('.filter-clear')) return;
            section.classList.toggle('open');
        });

        section.querySelector('.filter-clear').addEventListener('click', () => {
            filterSelected[k].clear();
            section.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
            const searchInput = section.querySelector('.filter-search input');
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('input'));
            updateFilterCount(k);
            if (k === 'country') {
                reloadDependentFilters();
            } else {
                loadMarkers();
            }
        });

        section.querySelector('.filter-search input').addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            section.querySelectorAll('.filter-option').forEach(opt => {
                const text = opt.textContent.toLowerCase();
                opt.style.display = text.includes(query) ? '' : 'none';
            });
        });
    });

    document.getElementById('btn-reset').addEventListener('click', () => {
        filterKeys.forEach(k => {
            filterSelected[k].clear();
            filterSections[k].querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
            filterSections[k].querySelectorAll('.filter-option').forEach(opt => opt.style.display = '');
            const searchInput = filterSections[k].querySelector('.filter-search input');
            searchInput.value = '';
            updateFilterCount(k);
        });
        reloadDependentFilters();
    });

    function updateFilterCount(k) {
        const count = filterSelected[k].size;
        const countEl = filterSections[k].querySelector('.filter-count');
        const clearBtn = filterSections[k].querySelector('.filter-clear');
        countEl.textContent = count > 0 ? ' (' + count + ')' : '';
        clearBtn.classList.toggle('visible', count > 0);
    }

    function hasActiveFilters() {
        return filterKeys.some(k => filterSelected[k].size > 0);
    }

    function buildFilterOptions(key, items) {
        const inner = filterSections[key].querySelector('.filter-options-inner');
        const searchInput = filterSections[key].querySelector('.filter-search input');
        searchInput.value = '';
        inner.innerHTML = '';
        items.forEach(item => {
            const label = document.createElement('label');
            label.className = 'filter-option';
            const checked = filterSelected[key].has(String(item.id));
            label.innerHTML = '<input type="checkbox" value="' + item.id + '"' + (checked ? ' checked' : '') + '> ' + esc(item.name);
            label.querySelector('input').addEventListener('change', (e) => {
                if (e.target.checked) {
                    filterSelected[key].add(String(item.id));
                } else {
                    filterSelected[key].delete(String(item.id));
                }
                updateFilterCount(key);
                if (key === 'country') {
                    reloadDependentFilters();
                } else {
                    loadMarkers();
                }
            });
            inner.appendChild(label);
        });
        const validIds = new Set(items.map(i => String(i.id)));
        for (const id of [...filterSelected[key]]) {
            if (!validIds.has(id)) filterSelected[key].delete(id);
        }
        updateFilterCount(key);
    }

    function reloadDependentFilters() {
        let url = FILTERS_URL;
        if (filterSelected.country.size > 0) {
            url += '?country=' + [...filterSelected.country].join(',');
        }
        fetch(url)
            .then(r => r.json())
            .then(data => {
                dependentKeys.forEach(k => {
                    buildFilterOptions(k, data[k] || []);
                });
                loadMarkers();
            });
    }

    // --- Server-side marker loading ---
    function buildFilterParams() {
        const params = new URLSearchParams();
        filterKeys.forEach(k => {
            if (filterSelected[k].size > 0) {
                params.set(k, [...filterSelected[k]].join(','));
            }
        });
        return params;
    }

    function loadMarkers() {
        markersLayer.clearLayers();
        if (!hasActiveFilters()) {
            allObjects = [];
            updateObjectCount(0);
            return;
        }

        if (fetchController) fetchController.abort();
        fetchController = new AbortController();

        const params = buildFilterParams();
        fetch(MARKERS_URL + '?' + params.toString(), { signal: fetchController.signal })
            .then(r => r.json())
            .then(data => {
                totalCount = data.total;
                allObjects = data.objects;
                renderMarkers();
            })
            .catch(e => {
                if (e.name !== 'AbortError') console.error(e);
            });
    }

    function renderMarkers() {
        markersLayer.clearLayers();
        const markers = [];
        allObjects.filter(obj => !hiddenIds.has(obj.id)).forEach(obj => {
            const tooltip = obj.name || 'Без названия';
            const popup = buildPopup(obj);

            if (obj.lat != null && obj.lng != null) {
                const m = L.marker([obj.lat, obj.lng]);
                m.bindTooltip(tooltip);
                m.bindPopup(popup);
                markers.push(m);
            } else if (obj.geom) {
                L.geoJSON(JSON.parse(obj.geom)).eachLayer(l => {
                    l.bindTooltip(tooltip);
                    l.bindPopup(popup);
                    markers.push(l);
                });
            }
        });
        markersLayer.addLayers(markers);
        updateObjectCount(markers.length);
    }

    function buildPopup(obj) {
        let html = '<div class="marker-popup">';
        html += '<b>' + esc(obj.name || 'Без названия') + '</b>';
        const fields = [
            ['Страна', obj.country_name],
            ['Гос. орган', obj.gov_org_name],
            ['Тип сил', obj.type_name],
            ['Вид сил', obj.kind_name],
            ['Ассоциация', obj.association_name],
            ['Часть', obj.unit_name],
        ];
        fields.forEach(([label, value]) => {
            if (value) html += '<br><span style="color:#888">' + esc(label) + ':</span> ' + esc(value);
        });
        if (obj.description) html += '<br><br>' + esc(obj.description);
        html += '<br><button class="popup-hide-btn" onclick="window._hideObject(' + obj.id + ')">Скрыть</button>';
        html += '</div>';
        return html;
    }

    // --- Hidden objects ---
    const hiddenPanel = document.getElementById('hidden-panel');
    const hiddenList = document.getElementById('hidden-list');

    window._hideObject = function(id) {
        const obj = allObjects.find(o => o.id === id);
        if (!obj) return;
        hiddenIds.add(id);
        hiddenObjects[id] = obj;
        map.closePopup();
        renderMarkers();
        renderHiddenPanel();
    };

    window._showObject = function(id) {
        hiddenIds.delete(id);
        delete hiddenObjects[id];
        renderMarkers();
        renderHiddenPanel();
    };

    function renderHiddenPanel() {
        if (hiddenIds.size === 0) {
            hiddenPanel.style.display = 'none';
            return;
        }
        hiddenPanel.style.display = 'block';
        hiddenList.innerHTML = '';
        for (const id of hiddenIds) {
            const obj = hiddenObjects[id];
            const item = document.createElement('div');
            item.className = 'hidden-item';
            item.innerHTML = '<span class="hidden-item-name">' + esc(obj.name || 'Без названия') + '</span>' +
                '<button class="hidden-item-show" onclick="window._showObject(' + id + ')" title="Показать">&times;</button>';
            hiddenList.appendChild(item);
        }
    }

    const objectCountEl = document.getElementById('object-count');

    function updateObjectCount(shown) {
        if (shown > 0) {
            objectCountEl.textContent = '(' + shown + ' из ' + totalCount + ')';
        } else {
            objectCountEl.textContent = '';
        }
    }

    // --- Load initial filter options ---
    fetch(FILTERS_URL)
        .then(r => r.json())
        .then(data => {
            filterKeys.forEach(k => {
                buildFilterOptions(k, data[k] || []);
            });
        });

    // --- Object search (server-side) ---
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    const searchClear = document.getElementById('search-clear');
    const searchMarkerLayer = L.layerGroup().addTo(map);
    let searchTimeout = null;

    searchClear.addEventListener('click', () => {
        searchInput.value = '';
        searchResults.style.display = 'none';
        searchResults.innerHTML = '';
        searchClear.classList.remove('visible');
        searchMarkerLayer.clearLayers();
    });

    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        const query = searchInput.value.trim();
        searchClear.classList.toggle('visible', searchInput.value.length > 0);
        if (query.length < 2) {
            searchResults.style.display = 'none';
            searchResults.innerHTML = '';
            return;
        }
        searchTimeout = setTimeout(() => {
            fetch(SEARCH_URL + '?q=' + encodeURIComponent(query))
                .then(r => r.json())
                .then(matches => {
                    searchResults.innerHTML = '';
                    if (matches.length === 0) {
                        searchResults.innerHTML = '<div class="search-no-results">Ничего не найдено</div>';
                    } else {
                        matches.forEach(obj => {
                            const div = document.createElement('div');
                            div.className = 'search-item';
                            div.innerHTML = '<div>' + esc(obj.name || 'Без названия') + '</div>' +
                                (obj.country_name ? '<div class="search-item-sub">' + esc(obj.country_name) + '</div>' : '');
                            div.addEventListener('click', () => {
                                searchMarkerLayer.clearLayers();
                                const popup = buildPopup(obj);
                                if (obj.lat != null && obj.lng != null) {
                                    const m = L.marker([obj.lat, obj.lng]).addTo(searchMarkerLayer);
                                    m.bindPopup(popup).openPopup();
                                    map.setView([obj.lat, obj.lng], 14);
                                } else if (obj.geom) {
                                    const layer = L.geoJSON(JSON.parse(obj.geom), {
                                        style: { color: '#ff6b6b', weight: 3 }
                                    }).addTo(searchMarkerLayer);
                                    layer.bindPopup(popup).openPopup();
                                    map.fitBounds(layer.getBounds());
                                }
                                searchResults.style.display = 'none';
                                searchInput.value = obj.name || '';
                            });
                            searchResults.appendChild(div);
                        });
                    }
                    searchResults.style.display = 'block';
                });
        }, 300);
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('#object-search')) {
            searchResults.style.display = 'none';
        }
    });

    // --- Export ---
    document.getElementById('btn-export').addEventListener('click', () => {
        if (allObjects.length === 0) {
            alert('Нет объектов для экспорта. Выберите фильтры.');
            return;
        }
        const format = document.getElementById('export-format').value;
        const headers = ['Название', 'Страна', 'Гос. орган', 'Тип сил', 'Вид сил', 'Ассоциация', 'Часть', 'Широта', 'Долгота', 'Описание'];
        const rows = allObjects.map(o => {
            let lat = o.lat, lng = o.lng;
            if (lat == null && lng == null && o.geom) {
                const bounds = L.geoJSON(JSON.parse(o.geom)).getBounds();
                const center = bounds.getCenter();
                lat = center.lat;
                lng = center.lng;
            }
            return [
                o.name || '', o.country_name || '', o.gov_org_name || '',
                o.type_name || '', o.kind_name || '', o.association_name || '',
                o.unit_name || '', lat != null ? lat : '', lng != null ? lng : '',
                o.description || ''
            ];
        });

        fetch(`${LOG_EXPORT_URL}?format=${format}&count=${allObjects.length}`).catch(() => {});

        if (format === 'csv') {
            const escape = v => '"' + String(v).replace(/"/g, '""') + '"';
            const csv = '\uFEFF' + [headers.map(escape).join(';')].concat(
                rows.map(r => r.map(escape).join(';'))
            ).join('\r\n');
            downloadFile(csv, 'objects.csv', 'text/csv;charset=utf-8');
        } else {
            const xmlHeader = '<?xml version="1.0" encoding="UTF-8"?>\n' +
                '<?mso-application progid="Excel.Sheet"?>\n' +
                '<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"\n' +
                ' xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">\n' +
                '<Worksheet ss:Name="Objects"><Table>\n';
            const xmlFooter = '</Table></Worksheet></Workbook>';
            const esc = v => String(v).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            let xml = xmlHeader;
            xml += '<Row>' + headers.map(h => '<Cell><Data ss:Type="String">' + esc(h) + '</Data></Cell>').join('') + '</Row>\n';
            rows.forEach(r => {
                xml += '<Row>' + r.map(v => {
                    const t = (typeof v === 'number') ? 'Number' : 'String';
                    return '<Cell><Data ss:Type="' + t + '">' + esc(v) + '</Data></Cell>';
                }).join('') + '</Row>\n';
            });
            xml += xmlFooter;
            downloadFile(xml, 'objects.xls', 'application/vnd.ms-excel');
        }
    });

    function downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // --- Show all hidden objects ---
    document.getElementById('btn-show-all').addEventListener('click', () => {
        hiddenIds.clear();
        Object.keys(hiddenObjects).forEach(k => delete hiddenObjects[k]);
        renderMarkers();
        renderHiddenPanel();
    });
})();
