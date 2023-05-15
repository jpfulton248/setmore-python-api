import requests
import json
import os
import datetime

class SetmoreCustomers:
	def __init__(self, auth):
		self.auth = auth

	def create_customer(self, customer_data):
		headers = {
			'Content-Type': 'application/json',
			'Authorization': f'Bearer {self.auth.access_token}'
		}

		try:
			response = requests.post('https://developer.setmore.com/api/v1/bookingapi/customer', headers=headers, json=customer_data)
			response.raise_for_status()
			data = response.json()
			customer_id = data.get('data', {}).get('customer_id')
			return customer_id
		except requests.exceptions.RequestException as e:
			print(f'Request failed: {e}')
		
		return None

	def get_customer_details(self, customer_id):
		headers = {
			'Content-Type': 'application/json',
			'Authorization': f'Bearer {self.auth.access_token}'
		}

		try:
			response = requests.get(f'https://developer.setmore.com/api/v1/bookingapi/customer/{customer_id}', headers=headers)
			response.raise_for_status()
			data = response.json()
			customer_details = data.get('data')
			return customer_details
		except requests.exceptions.RequestException as e:
			print(f'Request failed: {e}')
		
		return None