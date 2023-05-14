import requests
import json
import os

class SetmoreApi:
	def __init__(self, refresh_token_file='refresh_token.json', access_token_file='access_token.json', token_file_path='credentials'):
		"""
		Initializes SetmoreApi with necessary tokens

		:param refresh_token_file: (optional) Defaults to refresh_token.json
		:param access_token_file: (optional) Defaults to access_token.json
		:param token_file_path: (optional) Location for token json files. Defaults to directory 'credentials' as a subdirectory of current directory.
		"""
		self.refresh_token_file = os.path.join(token_file_path, refresh_token_file)
		self.access_token_file = os.path.join(token_file_path, access_token_file)
		self.refresh_token = None
		self.access_token = None
		self.token_path = None
	
		try:
			self.load_access_token()
		except FileNotFoundError:
			self.generate_access_token()

		self.verify_token()

	def load_token(self, token_file, token_key):
		with open(token_file, 'r') as file:
			data = json.load(file)
		return data[token_key]

	def load_refresh_token(self):
		self.refresh_token = self.load_token(self.refresh_token_file, 'refresh_token')

	def load_access_token(self):
		try:
			self.access_token = self.load_token(self.access_token_file, 'data')['token']['access_token']
		except FileNotFoundError:
			self.access_token = None

	def save_access_token(self, data):
		try:
			with open(self.access_token_file, 'w') as file:
				json.dump(data, file)
		except FileNotFoundError:
			self.generate_access_token()

	def generate_access_token(self):
		response = requests.get(f'https://developer.setmore.com/api/v1/o/oauth2/token?refreshToken={self.refresh_token}')
		if response.status_code == 200:
			data = response.json()
			try:
				self.save_access_token(data)
			except Exception as e:
				raise Exception(f'Access token generation successful, but saving failed: {str(e)}')
			exit
		else:
			raise Exception(f'Access token generation failed with status code: {response.status_code}\n{response.text}')

	def verify_token(self):
		try:
			self.load_refresh_token()

			if self.access_token is None:
				self.generate_access_token()

			headers = {
				'Content-Type': 'application/json',
				'Authorization': f'Bearer {self.access_token}'
			}

			services_response = requests.get('https://developer.setmore.com/api/v1/bookingapi/services', headers=headers)
			data = services_response.json()

			if services_response.status_code == 200:
				# Success: Access token is valid
				exit

			elif services_response.status_code == 401 and data.get('response', False) is False:
				# Unauthorized: Access token expired or invalid
				msg_value = data.get('msg', '')

				if 'access token either invalid / expired' in msg_value:
					# Request failed. Get a new access token
					self.generate_access_token()

				else:
					# Request failed for some other reason
					raise Exception(f'Request failed for a different reason with status code: {services_response.status_code} and text: {services_response.text}')

			else:
				# Request failed: Unknown error
				raise Exception(f'Testing auth key failed entirely')

		except requests.exceptions.RequestException as e:
			# Request exception occurred
			raise Exception(f'Request exception occurred: {str(e)}')


	def get_slots(self, staff_key=None, service_key=None, selected_date=None, off_hours=False, double_booking=False, slot_limit=None, timezone=None):
		self.verify_token()

		headers = {
			'Content-Type': 'application/json',
			'Authorization': f'Bearer {self.access_token}'
		}

		payload = {
			'staff_key': staff_key,
			'service_key': service_key,
			'selected_date': selected_date,
			'off_hours': off_hours,
			'double_booking': double_booking,
			'slot_limit': slot_limit,
			'timezone': timezone
		}

		response = requests.post('https://developer.setmore.com/api/v1/bookingapi/slots', headers=headers, json=payload)
		data = response.json()

		if response.status_code == 200:
			if 'data' in data and isinstance(data['data'], list):
				slots = data['data']
				if len(slots) == 0:
					return 'No available time slots for the given date range'
				else:
					return slots
			else:
				raise ValueError('Invalid response format')
		else:
			error_message = f'Request failed with status code {response.status_code}: {response.text}'
			raise ValueError(error_message)

		
	def get_services(self):
		self.verify_token()

		headers = {
			'Content-Type': 'application/json',
			'Authorization': f'Bearer {self.access_token}'
		}

		services_response = requests.get('https://developer.setmore.com/api/v1/bookingapi/services', headers=headers)
		data = services_response.json()

		if services_response.status_code == 200:
			services = data['data']['services']
			return services
		else:
			print(f'Request failed with status code {services_response.status_code}: {services_response.text}')
			exit