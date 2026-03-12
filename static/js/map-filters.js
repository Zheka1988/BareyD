(function() {
    const map = window.__map;
    if (!map) return;

    const FILTERS_URL = window.__FILTERS_URL;
    const MARKERS_URL = window.__MARKERS_URL;
    const SEARCH_URL = window.__SEARCH_URL;
    const esc = window.__esc;

    const markersLayer = window.__markersLayer;
    let fetchController = null;

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
            window.__allObjects = [];
            updateObjectCount(0);
            return;
        }

        if (fetchController) fetchController.abort();
        fetchController = new AbortController();

        const params = buildFilterParams();
        fetch(MARKERS_URL + '?' + params.toString(), { signal: fetchController.signal })
            .then(r => r.json())
            .then(data => {
                window.__totalCount = data.total;
                window.__allObjects = data.objects;
                window.__renderMarkers();
            })
            .catch(e => {
                if (e.name !== 'AbortError') console.error(e);
            });
    }

    window.__renderMarkers = function() {
        markersLayer.clearLayers();
        const markers = [];
        window.__allObjects.filter(obj => !window.__hiddenIds.has(obj.id)).forEach(obj => {
            const tooltip = obj.name || 'Без названия';
            const popup = window.__buildPopup(obj);

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
    };

    window.__buildPopup = function(obj) {
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
    };

    const objectCountEl = document.getElementById('object-count');
    function updateObjectCount(shown) {
        if (shown > 0) {
            objectCountEl.textContent = '(' + shown + ' из ' + window.__totalCount + ')';
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
                                const popup = window.__buildPopup(obj);
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
})();
