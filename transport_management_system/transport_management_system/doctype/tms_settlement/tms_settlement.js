frappe.ui.form.on('TMS Settlement', {
    refresh: function(frm) {
        // Add Calculate button
        frm.add_custom_button(__('Calculate Pay'), function() {
            frm.save(); // The validate hook in python calculates the pay
        }, __('Actions'));

        // Add Generate Invoice button if submitted
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Generate Purchase Invoice'), function() {
                frappe.call({
                    method: 'generate_purchase_invoice',
                    doc: frm.doc,
                    callback: function(r) {
                        if (!r.exc) {
                            frappe.set_route('Form', 'Purchase Invoice', r.message);
                        }
                    }
                });
            }, __('Actions'));
        }
    }
});
