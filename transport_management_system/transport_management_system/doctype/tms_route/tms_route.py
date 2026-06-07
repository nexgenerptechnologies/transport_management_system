import frappe
from frappe.model.document import Document
import requests

class TMSRoute(Document):
	def validate(self):
		self.calculate_route_metrics()
		
	def calculate_route_metrics(self):
		if not self.start_location or not self.end_location:
			return
			
		# Expecting locations as "lon,lat"
		coords = [self.start_location]
		
		# Add intermediate stops
		for stop in self.stops:
			if stop.location:
				coords.append(stop.location)
				
		coords.append(self.end_location)
		
		coordinates_str = ";".join(coords)
		
		try:
			url = f"http://router.project-osrm.org/route/v1/driving/{coordinates_str}?overview=false"
			response = requests.get(url, timeout=10)
			
			if response.status_code == 200:
				data = response.json()
				if data.get("routes") and len(data["routes"]) > 0:
					route = data["routes"][0]
					# OSRM returns distance in meters and duration in seconds
					self.total_estimated_distance = route.get("distance", 0) / 1000.0
					self.total_estimated_time = route.get("duration", 0) / 3600.0
			else:
				frappe.msgprint(f"OSRM API Error: {response.status_code}")
		except Exception as e:
			frappe.log_error(message=str(e), title="OSRM Routing Error")
			frappe.msgprint("Could not calculate route metrics from OSRM. Ensure coordinates are in 'lon,lat' format.")
