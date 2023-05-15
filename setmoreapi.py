#setmoreapi.py
import requests
import json
import os

class SetmoreAuth:
	"""
	Initializes SetmoreApi with necessary tokens

	:param refresh_token_file: (optional) Defaults to refresh_token.json
	:param access_token_file: (optional) Defaults to access_token.json
	:param token_file_path: (optional) Location for token json files. Defaults to directory 'credentials' as a subdirectory of current directory.
	"""
	def __init__(self, refresh_token_file='refresh_token.json', access_token_file='access_token.json', token_file_path='credentials'):
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

class Setmore:
	def __init__(self, auth):
		self.auth = auth
		self.services = SetmoreServices(self.auth)
		self.staff = SetmoreStaff(self.auth)
		self.timeslots = SetmoreTimeSlots(self.auth)
		self.customers = SetmoreCustomers(self.auth)
		self.appointments = SetmoreAppointments(self.auth)

class SetmoreServices:
	def __init__(self, auth):
		self.auth = auth

	def get_services(self, save=False, file=None):
		headers = {
			'Content-Type': 'application/json',
			'Authorization': f'Bearer {self.auth.access_token}'
		}

		try:
			services_response = requests.get('https://developer.setmore.com/api/v1/bookingapi/services', headers=headers)
			services_response.raise_for_status()
			data = services_response.json()
			services = data['data']['services']

			if save:
				self.save_services_data(services, file)

			return services

		except requests.exceptions.RequestException as e:
			print(f'Request failed: {e}')

		except KeyError as e:
			print(f'Invalid response format: {e}')

		return None

	def save_services_data(self, services, file=None):
		if file:
			if not os.path.isabs(file):
				default_path = os.path.join('credentials', file)
				file = os.path.abspath(default_path)
		else:
			file = os.path.abspath(os.path.join('credentials', 'services.json'))

		try:
			with open(file, 'w') as f:
				json.dump(services, f, indent=4)
			print(f'Services data saved to {file}')
		except Exception as e:
			print(f'Failed to save services data: {str(e)}')

class SetmoreStaff:
	def __init__(self, auth):
		self.auth = auth

	def get_all_staff(self, save=False, file='credentials/staff.json'):
		headers = {
			'Content-Type': 'application/json',
			'Authorization': f'Bearer {self.auth.access_token}'
		}

		try:
			response = requests.get('https://developer.setmore.com/api/v1/bookingapi/staffs', headers=headers)
			response.raise_for_status()
			data = response.json()
			staff = data['data']['staffs']

			if save:
				self.save_staff_data(staff, file)

			return staff
		except requests.exceptions.RequestException as e:
			print(f'Request failed: {e}')
		except KeyError as e:
			print(f'Invalid response format: {e}')

		return None

	def save_staff_data(self, staff, file):
		try:
			with open(file, 'w') as f:
				json.dump(staff, f, indent=4)
			print(f'Staff data saved to {file}')
		except Exception as e:
			print(f'Failed to save staff data: {str(e)}')
	

class SetmoreTimeSlots:
	def __init__(self, auth):
		self.auth = auth

	def get_all_available_time_slots(self, staff_key=None, service_key=None, selected_date=None, off_hours=False, double_booking=False, slot_limit=None, timezone=None):
		headers = {
			'Content-Type': 'application/json',
			'Authorization': f'Bearer {self.auth.access_token}'
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

		try:
			response = requests.post('https://developer.setmore.com/api/v1/bookingapi/slots', headers=headers, json=payload)
			response.raise_for_status()
			data = response.json()
			slots = data.get('data', [])
			return slots
		except requests.exceptions.RequestException as e:
			print(f'Request failed: {e}')
		except KeyError as e:
			print(f'Invalid response format: {e}')

		return None
	
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


class SetmoreAppointments:
	def __init__(self, auth):
		self.auth = auth

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