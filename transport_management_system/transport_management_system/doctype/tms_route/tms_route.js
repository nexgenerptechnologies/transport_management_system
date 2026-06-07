frappe.ui.form.on('TMS Route', {
    refresh: function(frm) {
        if (!frm.doc.__islocal) {
            frm.add_custom_button(__('Refresh Map'), function() {
                frm.events.render_map(frm);
            }, __('Actions'));
            
            setTimeout(() => {
                frm.events.render_map(frm);
            }, 500);
        }
    },
    
    render_map: function(frm) {
        let $wrapper = frm.get_field('stops').$wrapper;
        let map_id = 'leaflet-map-' + frm.doc.name;
        
        if ($wrapper.find('#' + map_id).length === 0) {
            $('<div id="' + map_id + '" style="height: 400px; width: 100%; border: 1px solid #d1d8dd; border-radius: 4px; margin-bottom: 15px; z-index: 1;"></div>').insertBefore($wrapper.find('.grid-wrapper'));
        }
        
        frappe.require([
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
        ], function() {
            if (frm.map_instance) {
                frm.map_instance.remove();
            }
            
            frm.map_instance = L.map(map_id).setView([20.5937, 78.9629], 5); // Default center India
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(frm.map_instance);
            
            let bounds = [];
            
            let locations_to_plot = [];
            if (frm.doc.start_location) locations_to_plot.push({loc: frm.doc.start_location, title: 'Start: ' + frm.doc.start_location});
            
            frm.doc.stops.forEach(function(stop) {
                if (stop.location) locations_to_plot.push({loc: stop.location, title: 'Stop ' + stop.stop_sequence + ': ' + stop.location});
            });
            
            if (frm.doc.end_location) locations_to_plot.push({loc: frm.doc.end_location, title: 'End: ' + frm.doc.end_location});

            locations_to_plot.forEach(function(item) {
                frappe.call({
                    method: 'geocode_location',
                    doc: frm.doc,
                    args: { location_name: item.loc },
                    callback: function(r) {
                        if (r.message) {
                            let parts = r.message.split(',');
                            let lon = parseFloat(parts[0]);
                            let lat = parseFloat(parts[1]);
                            if (lat && lon) {
                                let marker = L.marker([lat, lon]).addTo(frm.map_instance);
                                marker.bindPopup(`<b>${item.title}</b>`);
                                bounds.push([lat, lon]);
                                frm.map_instance.fitBounds(bounds, {padding: [50, 50]});
                            }
                        }
                    }
                });
            });
        });
    }
});
