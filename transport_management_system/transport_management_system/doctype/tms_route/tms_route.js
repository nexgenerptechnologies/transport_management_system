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
        // Find or create a map container above the stops table
        let $wrapper = frm.get_field('stops').$wrapper;
        let map_id = 'leaflet-map-' + frm.doc.name;
        
        if ($wrapper.find('#' + map_id).length === 0) {
            $('<div id="' + map_id + '" style="height: 400px; width: 100%; border: 1px solid #d1d8dd; border-radius: 4px; margin-bottom: 15px; z-index: 1;"></div>').insertBefore($wrapper.find('.grid-wrapper'));
        }
        
        // Load Leaflet dynamically if not loaded
        frappe.require([
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
        ], function() {
            if (frm.map_instance) {
                frm.map_instance.remove();
            }
            
            // Initialize map
            frm.map_instance = L.map(map_id).setView([0, 0], 2);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(frm.map_instance);
            
            // Collect stops and geocode them (Simulated using Frappe's built-in geocoding or basic search)
            let bounds = [];
            
            frm.doc.stops.forEach(function(stop, index) {
                if (stop.location) {
                    // For a real production app, we would use a geocoding API or a custom coordinate field.
                    // Since Frappe locations are usually addresses, we'll fetch coordinates if available in an Address doctype
                    // Here we will just simulate plotting if we had coords, or use a basic search.
                    
                    frappe.call({
                        method: 'frappe.geo.utils.get_coords',
                        args: { name: stop.location }, // Assume location is an Address name
                        callback: function(r) {
                            if (r.message) {
                                let lat = r.message.latitude;
                                let lon = r.message.longitude;
                                if (lat && lon) {
                                    let marker = L.marker([lat, lon]).addTo(frm.map_instance);
                                    marker.bindPopup(`<b>Stop ${stop.stop_sequence}</b><br>${stop.location}<br>${stop.stop_type}`);
                                    bounds.push([lat, lon]);
                                    frm.map_instance.fitBounds(bounds);
                                }
                            }
                        }
                    });
                }
            });
            
            // Example default fallback coordinates if geocoding is slow or empty (just for visual representation)
            if (bounds.length === 0) {
                // Try some dummy coordinates if none exist, so the user sees *something*
                let d_lat = 40.7128 + (Math.random() * 0.1);
                let d_lon = -74.0060 + (Math.random() * 0.1);
                let m1 = L.marker([d_lat, d_lon]).addTo(frm.map_instance);
                m1.bindPopup("Demo Stop 1");
                frm.map_instance.setView([d_lat, d_lon], 10);
            }
        });
    }
});
