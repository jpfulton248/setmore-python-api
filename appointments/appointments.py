import requests
import json
import os
import datetime
from setmore_auth import SetmoreAuth

class SetmoreAppointments:
	def __init__(self):
		self.auth = SetmoreAuth()

	def create_appointment(self, appointment_data):
		headers = {
			'Content-Type': 'application/json',
			'Authorization': f'Bearer {self.auth.access_token}'
		}

		try:
			response = requests.post('https://developer.setmore.com/api/v1/bookingapi/appointments', headers=headers, json=appointment_data)
			response.raise_for_status()
			data = response.json()
			appointment_id = data.get('data', {}).get('appointment_id')
			return appointment_id
		except requests.exceptions.RequestException as e:
			print(f'Request failed: {e}')
		
		return None

	def update_appointment_label(self, appointment_id, label):
		headers = {
			'Content-Type': 'application/json',
			'Authorization': f'Bearer {self.auth.access_token}'
		}

		payload = {
			'label': label
		}

		try:
			response = requests.put(f'https://developer.setmore.com/api/v1/bookingapi/appointments/{appointment_id}', headers=headers, json=payload)
			response.raise_for_status()
			data = response.json()
			return data
		except requests.exceptions.RequestException as e:
			print(f'Request failed: {e}')
		
		return None

	def get_appointments(self):
		headers = {
			'Content-Type': 'application/json',
			'Authorization': f'Bearer {self.auth.access_token}'
		}

		try:
			response = requests.get('https://developer.setmore.com/api/v1/bookingapi/appointments', headers=headers)
			response.raise_for_status()
			data = response.json()
			appointments = data.get('data', [])
			return appointments
		except requests.exceptions.RequestException as e:
			print(f'Request failed: {e}')
		
		return None