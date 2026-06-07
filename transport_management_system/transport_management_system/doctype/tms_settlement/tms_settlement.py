import frappe
from frappe.model.document import Document

class TMSSettlement(Document):
	def validate(self):
		self.calculate_pay()
		
	def calculate_pay(self):
		# Fetch the contract for this driver
		contract_name = frappe.db.get_value("TMS Driver Contract", {"driver": self.driver}, "name")
		if not contract_name:
			frappe.throw(f"No active Driver Contract found for {self.driver}")
			
		contract = frappe.get_doc("TMS Driver Contract", contract_name)
		
		total_distance = 0
		total_drops = 0
		
		# If a dispatch is linked, calculate distance and drops based on route
		if self.dispatch:
			dispatch_doc = frappe.get_doc("TMS Dispatch", self.dispatch)
			if dispatch_doc.route:
				route_doc = frappe.get_doc("TMS Route", dispatch_doc.route)
				total_distance = route_doc.total_estimated_distance or 0
				total_drops = len([s for s in route_doc.stops if s.stop_type == "Delivery"])
				
		self.total_distance_pay = (total_distance * contract.rate_per_km) if contract.rate_per_km else 0
		self.total_drop_pay = (total_drops * contract.rate_per_drop) if contract.rate_per_drop else 0
		self.base_pay = contract.fixed_base_pay or 0
		
		# Calculate total deductions
		self.total_deductions = sum([d.amount for d in self.deductions])
		
		# Calculate Gross and Net
		self.gross_pay = self.total_distance_pay + self.total_drop_pay + self.base_pay
		self.net_pay = self.gross_pay - self.total_deductions
