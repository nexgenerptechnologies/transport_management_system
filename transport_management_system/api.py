import frappe
import json

@frappe.whitelist(allow_guest=True)
def telematics_webhook():
	"""
	Endpoint for external telematics providers to push GPS data.
	Expected Header: X-Telematics-API-Key: <webhook_secret>
	Expected Payload: {"vehicle": "VH-01", "latitude": "...", "longitude": "...", "odometer": 100, "speed": 60, "engine_status": "On"}
	"""
	headers = frappe.request.headers
	api_key = headers.get("X-Telematics-API-Key")
	
	settings = frappe.get_single("Telematics Provider Settings")
	if not settings.webhook_secret or settings.webhook_secret != api_key:
		frappe.throw("Unauthorized", frappe.PermissionError)
		
	data = frappe.request.get_data(as_text=True)
	if not data:
		return {"status": "error", "message": "No payload provided"}
		
	try:
		payload = json.loads(data)
		
		# Validate vehicle exists
		vehicle = payload.get("vehicle")
		if not frappe.db.exists("Vehicle", vehicle):
			return {"status": "error", "message": f"Vehicle {vehicle} not found in system"}
			
		log = frappe.new_doc("Vehicle Telemetry Log")
		log.vehicle = vehicle
		log.timestamp = frappe.utils.now()
		log.latitude = payload.get("latitude")
		log.longitude = payload.get("longitude")
		log.odometer = payload.get("odometer", 0.0)
		log.speed = payload.get("speed", 0.0)
		log.engine_status = payload.get("engine_status", "On")
		
		log.insert(ignore_permissions=True)
		frappe.db.commit()
		
		return {"status": "success", "message": "Telemetry logged successfully", "log_id": log.name}
		
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(message=str(e), title="Telematics Webhook Error")
		return {"status": "error", "message": str(e)}
