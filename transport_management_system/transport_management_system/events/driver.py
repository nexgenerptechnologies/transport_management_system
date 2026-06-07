import frappe

def create_supplier_for_driver(doc, method):
    """
    Automatically creates a Supplier record when a new Driver is added.
    Links the Supplier back to the Driver if possible, or just uses the same name.
    """
    # Check if a supplier already exists with this name
    if frappe.db.exists("Supplier", doc.full_name):
        return

    # Create the supplier
    supplier = frappe.get_doc({
        "doctype": "Supplier",
        "supplier_name": doc.full_name,
        "supplier_group": "Local",  # Defaulting to Local, user can change later
        "supplier_type": "Company" # Or Individual
    })
    
    # Try to set supplier group to Transporter if it exists
    if frappe.db.exists("Supplier Group", "Transporter"):
        supplier.supplier_group = "Transporter"
        
    supplier.insert(ignore_permissions=True)
    frappe.msgprint(f"Automatically created Supplier: {supplier.name} for Driver: {doc.full_name}")
