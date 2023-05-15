import requests
import json
import os
import datetime
from setmore_auth import SetmoreAuth

class SetmoreServices:
	def __init__(self):
		self.auth = SetmoreAuth()

	def get_services(self):
		headers = {
			'Content-Type': 'application/json',
			'Authorization': f'Bearer {self.auth.access_token}'
		}

		try:
			services_response = requests.get('https://developer.setmore.com/api/v1/bookingapi/services', headers=headers)
			services_response.raise_for_status()
			data = services_response.json()
			services = data['data']['services']
			return services
		except requests.exceptions.RequestException as e:
			print(f'Request failed: {e}')
		except KeyError as e:
			print(f'Invalid response format: {e}')

		return None