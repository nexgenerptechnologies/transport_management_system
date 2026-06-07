import frappe
from frappe.model.document import Document
import requests
import re

class TMSRoute(Document):
	def validate(self):
		self.calculate_route_metrics()
		
	@frappe.whitelist()
	def geocode_location(self, location_name):
		# If it's already a coordinate (e.g. 77.2,28.6)
		if re.match(r'^-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?$', location_name):
			return location_name.replace(' ', '')
			
		# Otherwise, geocode using OpenStreetMap Nominatim
		try:
			url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json&limit=1"
			headers = {'User-Agent': 'Frappe-TMS-App'}
			response = requests.get(url, headers=headers, timeout=5)
			if response.status_code == 200:
				data = response.json()
				if data and len(data) > 0:
					# Nominatim returns lat and lon, OSRM expects lon,lat
					lon = data[0].get('lon')
					lat = data[0].get('lat')
					return f"{lon},{lat}"
		except Exception as e:
			frappe.log_error(message=str(e), title="Geocoding Error")
			
		return None

	def calculate_route_metrics(self):
		if not self.start_location or not self.end_location:
			return
			
		# Geocode start
		start_coord = self.geocode_location(self.start_location)
		if not start_coord:
			frappe.msgprint(f"Could not find coordinates for Start Location: {self.start_location}")
			return
			
		coords = [start_coord]
		
		# Geocode intermediate stops
		for stop in self.stops:
			if stop.location:
				coord = self.geocode_location(stop.location)
				if coord:
					coords.append(coord)
				else:
					frappe.msgprint(f"Could not find coordinates for Stop: {stop.location}")
					return
					
		# Geocode end
		end_coord = self.geocode_location(self.end_location)
		if not end_coord:
			frappe.msgprint(f"Could not find coordinates for End Location: {self.end_location}")
			return
			
		coords.append(end_coord)
		
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
				frappe.msgprint(f"OSRM API Error: {response.status_code} - {response.text}")
		except Exception as e:
			frappe.log_error(message=str(e), title="OSRM Routing Error")
			frappe.msgprint("Could not calculate route metrics from OSRM.")
