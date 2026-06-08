app_name = "transport_management_system"
app_title = "Transportation Management System (TMS) & Advanced Fleet Operations app for ERPNext"
app_publisher = "NexGen ERP Technologies"
app_description = "Transportation Management System (TMS) & Advanced Fleet Operations app for ERPNext"
app_email = "admin@example.com"
app_license = "mit"

doc_events = {
    'TMS Driver': {
        'after_insert': 'transport_management_system.transport_management_system.events.driver.create_supplier_for_driver'
    }
}
