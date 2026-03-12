(function() {
    const LOG_EXPORT_URL = window.__LOG_EXPORT_URL;

    document.getElementById('btn-export').addEventListener('click', () => {
        if (window.__allObjects.length === 0) {
            alert('Нет объектов для экспорта. Выберите фильтры.');
            return;
        }
        const format = document.getElementById('export-format').value;
        const headers = ['Название', 'Страна', 'Гос. орган', 'Тип сил', 'Вид сил', 'Ассоциация', 'Часть', 'Широта', 'Долгота', 'Описание'];
        const rows = window.__allObjects.map(o => {
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

        fetch(LOG_EXPORT_URL + '?format=' + format + '&count=' + window.__allObjects.length).catch(() => {});

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
})();
