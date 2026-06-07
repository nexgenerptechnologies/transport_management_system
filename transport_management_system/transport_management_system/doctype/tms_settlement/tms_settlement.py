import frappe
from frappe.model.document import Document

class TMSSettlement(Document):
    def validate(self):
        self.calculate_pay()
        
    def calculate_pay(self):
        # Calculate gross pay based on Dispatch and Contract
        if not self.driver or not self.dispatch:
            return
            
        # Get active contract
        contract_name = frappe.db.get_value("TMS Driver Contract", {"driver": self.driver, "status": "Active"}, "name")
        if not contract_name:
            # Maybe they didn't set a contract, just default to 0
            pay_per_distance = 0
            pay_per_drop = 0
        else:
            contract = frappe.get_doc("TMS Driver Contract", contract_name)
            pay_per_distance = contract.pay_per_distance or 0
            pay_per_drop = contract.pay_per_drop or 0
            
        dispatch_doc = frappe.get_doc("TMS Dispatch", self.dispatch)
        if not dispatch_doc.route:
            return
            
        route_doc = frappe.get_doc("TMS Route", dispatch_doc.route)
        
        distance = route_doc.total_estimated_distance or 0
        drops = len([s for s in route_doc.stops if s.stop_type == "Delivery"])
        
        self.total_distance_pay = distance * pay_per_distance
        self.total_drop_pay = drops * pay_per_drop
        self.base_pay = self.total_distance_pay + self.total_drop_pay
        
        self.total_deductions = sum([d.amount for d in self.deductions])
        
        self.gross_pay = self.base_pay
        self.net_pay = self.gross_pay - self.total_deductions

    @frappe.whitelist()
    def generate_purchase_invoice(self):
        if not self.docstatus == 1:
            frappe.throw("Please submit the settlement first.")
            
        # Find supplier linked to driver
        supplier = frappe.db.get_value("Supplier", {"supplier_name": self.driver})
        if not supplier:
            frappe.throw(f"No Supplier record found for Driver '{self.driver}'. Please create one to generate invoices.")
            
        # Create Purchase Invoice
        pi = frappe.new_doc("Purchase Invoice")
        pi.supplier = supplier
        
        # Net Pay Item
        pi.append("items", {
            "item_name": "Driver Settlement",
            "description": f"Net Settlement Pay for Dispatch {self.dispatch} (Base: {self.base_pay}, Deductions: {self.total_deductions})",
            "qty": 1,
            "rate": self.net_pay,
            "expense_account": frappe.db.get_value("Company", frappe.defaults.get_user_default("Company"), "default_expense_account") or ""
        })
        
        pi.insert(ignore_permissions=True)
        frappe.msgprint(f"Generated Purchase Invoice: <a href='/app/purchase-invoice/{pi.name}'>{pi.name}</a>")
        return pi.name
