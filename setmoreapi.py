#setmoreapi.py
import requests
import json
import os
from datetime import date, timedelta, datetime
import time

import os
import json
import requests
import time


class SetmoreAuth:
	"""
	Initializes SetmoreApi with necessary tokens

	:param refresh_token_file: (optional) Defaults to refresh_token.json
	:param access_token_file: (optional) Defaults to access_token.json
	:param token_file_path: (optional) Location for token json files. Defaults to directory 'credentials' as a subdirectory of current directory.
	"""
	def __init__(self, refresh_token_file='refresh_token.json', access_token_file='access_token.json',
				 token_file_path='credentials'):
		self.token_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), token_file_path)
		self.refresh_token_file = os.path.join(self.token_file_path, refresh_token_file)
		self.access_token_file = os.path.join(self.token_file_path, access_token_file)
		self.refresh_token = None
		self.access_token = None

		try:
			self.load_refresh_token()  # Retrieve refresh token before attempting to generate or load access token
		except FileNotFoundError:
			raise FileNotFoundError("Could not load refresh token")

		try:
			if os.path.isfile(self.access_token_file):
				with open(self.access_token_file, 'r') as file:
					json_data = file.read()
					data = json.loads(json_data)

					expiration_time = data['data']['token']['expires']
					current_time = int(time.time())

					if expiration_time - current_time <= 4 * 3600:  # 4 hours in seconds
						self.generate_access_token()
		except FileNotFoundError:
			self.generate_access_token()

		try:
			self.load_access_token()
		except FileNotFoundError:
			self.generate_access_token()

	def save_access_token(self, data):
		try:
			with open(self.access_token_file, 'w') as file:
				json.dump(data, file)
		except FileNotFoundError:
			raise FileNotFoundError("Error on write access_token_file. File or file path not found")

	def generate_access_token(self):
		response = requests.get(f'https://developer.setmore.com/api/v1/o/oauth2/token?refreshToken={self.refresh_token}')

		if response.status_code == 200:
			data = response.json()
			try:
				self.save_access_token(data)
				self.load_access_token()
			except Exception as e:
				raise Exception(f'Access token generation successful, but saving failed: {str(e)}')
		else:
			raise Exception(f'Access token generation failed with status code: {response.status_code}\n{response.text}')

	def load_refresh_token(self):
		try:
			with open(self.refresh_token_file, 'r') as file:
				data = json.load(file)
			self.refresh_token = data['refresh_token']
		except FileNotFoundError:
			self.refresh_token = None
			raise FileNotFoundError("Refresh token file not found")

	def load_access_token(self):
		try:
			with open(self.access_token_file, 'r') as file:
				data = json.load(file)
			self.access_token = data['data']['token']['access_token']
		except FileNotFoundError:
			self.access_token = None
			raise FileNotFoundError("Access token file not found")


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
		self.make_request

	def make_request(self, url, headers, method, json=None):
		""" Make a request
		``url (required, str)`` url
		``headers (required, str)`` headers in a json string
		``method (required, str)`` get or post
		``payload (optional, str)`` payload in a json string
		"""
		# Depending on the HTTP method (get, post, etc.), we may need to handle data differently.
		if method.lower() == 'get':
			request_func = requests.get
		elif method.lower() == 'post':
			request_func = requests.post

		if json is not None:
			response = request_func(url, headers=headers, json=json) #type: ignore

			if response.status_code == 401:
				# Unauthorized. Refresh the token and try again.
				self.auth.generate_access_token()
				headers['Authorization'] = f'Bearer {self.auth.access_token}'  # Update the headers with the new token.
				response = request_func(url, headers=headers, json=json) #type: ignore
		else:
			response = request_func(url, headers=headers) #type: ignore

			if response.status_code == 401:
				# Unauthorized. Refresh the token and try again.
				self.auth.generate_access_token()
				headers['Authorization'] = f'Bearer {self.auth.access_token}'  # Update the headers with the new token.
				response = request_func(url, headers=headers) #type: ignore
		return response
	
	def get_services_all(self, save=False, file=None):
		headers = {
			'Content-Type': 'application/json',
			'Authorization': f'Bearer {self.auth.access_token}'
		}

		try:
			services_response = self.make_request('https://developer.setmore.com/api/v1/bookingapi/services', headers, 'get')
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
				default_path = os.path.join(self.auth.token_file_path, file)
				file = os.path.abspath(default_path)
		else:
			file = os.path.abspath(os.path.join(self.auth.token_file_path, 'services.json'))

		try:
			with open(file, 'w') as f:
				json.dump(services, f, indent=4)
			print(f'Services data saved to {file}')
		except Exception as e:
			print(f'Failed to save services data: {str(e)}')

class SetmoreStaff:
	def __init__(self, auth):
		self.auth = auth
		self.make_request = self.make_request

	def make_request(self, url, headers, method, json=None):
		""" Make a request
		``url (required, str)`` url
		``headers (required, str)`` headers in a json string
		``method (required, str)`` get or post
		``payload (optional, str)`` payload in a json string
		"""
		# Depending on the HTTP method (get, post, etc.), we may need to handle data differently.
		if method.lower() == 'get':
			request_func = requests.get
		elif method.lower() == 'post':
			request_func = requests.post

		if json is not None:
			response = request_func(url, headers=headers, json=json) #type: ignore

			if response.status_code == 401:
				# Unauthorized. Refresh the token and try again.
				self.auth.generate_access_token()
				headers['Authorization'] = f'Bearer {self.auth.access_token}'  # Update the headers with the new token.
				response = request_func(url, headers=headers, json=json) #type: ignore
		else:
			response = request_func(url, headers=headers) #type: ignore

			if response.status_code == 401:
				# Unauthorized. Refresh the token and try again.
				self.auth.generate_access_token()
				headers['Authorization'] = f'Bearer {self.auth.access_token}'  # Update the headers with the new token.
				response = request_func(url, headers=headers) #type: ignore
		return response

	def get_all_staff(self, save=False, file=None):
		headers = {
			'Content-Type': 'application/json',
			'Authorization': f'Bearer {self.auth.access_token}'
		}

		try:
			response = self.make_request('https://developer.setmore.com/api/v1/bookingapi/staffs', headers=headers, method='get')
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
		if file:
			if not os.path.isabs(file):
				default_path = os.path.join(self.auth.token_file_path, file)
				file = os.path.abspath(default_path)
		else:
			file = os.path.abspath(os.path.join(self.auth.token_file_path, 'staff.json'))

		try:
			with open(file, 'w') as f:
				json.dump(staff, f, indent=4)
			print(f'Staff data saved to {file}')
		except Exception as e:
			print(f'Failed to save staff data: {str(e)}')

def mdy_to_dmy(date_str):
	return datetime.strftime(datetime.strptime(date_str, '%m/%d/%Y'), '%d/%m/%Y')

def dmy_to_mdy(date_str):
	return datetime.strftime(datetime.strptime(date_str, '%d/%m/%Y'), '%m/%d/%Y')

class SetmoreTimeSlots:
	def __init__(self, auth):
		self.auth = auth
		self.make_request = self.make_request

	def make_request(self, url, headers, method, json=None):
		""" Make a request
		``url (required, str)`` url
		``headers (required, str)`` headers in a json string
		``method (required, str)`` get or post
		``payload (optional, str)`` payload in a json string
		"""
		# Depending on the HTTP method (get, post, etc.), we may need to handle data differently.
		if method.lower() == 'get':
			request_func = requests.get
		elif method.lower() == 'post':
			request_func = requests.post

		if json is not None:
			response = request_func(url, headers=headers, json=json) #type: ignore

			if response.status_code == 401:
				# Unauthorized. Refresh the token and try again.
				self.auth.generate_access_token()
				headers['Authorization'] = f'Bearer {self.auth.access_token}'  # Update the headers with the new token.
				response = request_func(url, headers=headers, json=json) #type: ignore
		else:
			response = request_func(url, headers=headers) #type: ignore

			if response.status_code == 401:
				# Unauthorized. Refresh the token and try again.
				self.auth.generate_access_token()
				headers['Authorization'] = f'Bearer {self.auth.access_token}'  # Update the headers with the new token.
				response = request_func(url, headers=headers) #type: ignore
		return response

	def get_all_available_time_slots(self, service_name=None, staff_key=None, service_key=None, selected_date=None, off_hours=False, double_booking=False, slot_limit=None, timezone=None, past=False):
		"""
		Get all available time slots for the given service, staff, and date.

		Parameters
		----------
		``service_name (str, required)``: The name of the service. Default is to None. (optional if service_key is provided)

		``staff_key (str, optional)``: The key of the staff_key of the given staff_member. Default is to pull the first staff_key from the services.json file if it exists.

		``service_key (str, optional)``: The key of the service. Default is None. Required if service_name is not provided.

		``selected_date (str, optional)``: The selected date in "MM/DD/YYYY" format. Default is today's date.

		``off_hours (bool, optional)``: A boolean indicating whether to include off-hours slots. Default is False.

		``double_booking (bool, optional)``: A boolean indicating whether to allow double booking. Default is False.

		``slot_limit (int, optional)``: The maximum number of slots to retrieve. Default is None.

		``timezone (str, optional)``: The timezone for the slots. Default is None.

		``past (bool, required)``: Show time slots that are in the past. Default is None.

		Returns
		-------
		A list of available time slots.
		:rtype: list
		"""

		headers = {
			'Content-Type': 'application/json',
			'Authorization': f'Bearer {self.auth.access_token}'
		}
		if os.path.isfile(os.path.join(self.auth.token_file_path, 'services.json')):
			with open(os.path.join(self.auth.token_file_path, 'services.json')) as file:
				data = json.load(file)
				if staff_key is None:
					for service in data:
						if service["service_name"] == service_name:
							staff_key = service["staff_keys"][0]
							break
				if service_key is None:
					for service in data:
						if service["service_name"] == service_name:
							service_key = service["key"]
							service_duration = service["duration"]
							break
		if service_key is None and service_name is None:
			error = 'Either service_key or service_name must be provided'
			raise Exception(error)
		if selected_date is None:
			selected_date = date.today().strftime("%d/%m/%Y")
		else:
			selected_date = mdy_to_dmy(selected_date)

		payload = {
			key: value
			for key, value in {
				"staff_key": staff_key,
				"service_key": service_key,
				"selected_date": selected_date,
				"off_hours": off_hours,
				"double_booking": double_booking,
				"slot_limit": slot_limit,
				"timezone": timezone
			}.items()
			if value is not None
		}
		selected_date = datetime.strptime(selected_date, '%d/%m/%Y')
		try:
			response = self.make_request('https://developer.setmore.com/api/v1/bookingapi/slots', headers, 'post', json=payload)
			response.raise_for_status()
			data = response.json()
			time_slots = data['data'].get('slots')

			dt_time_slots = [selected_date + timedelta(hours=int(time.split('.')[0]), minutes=int(time.split('.')[1]))
			for time in time_slots
			if past or (selected_date + timedelta(hours=int(time.split('.')[0]), minutes=int(time.split('.')[1]))) >= datetime.now()]
			dt_str_time_slots = [dt_str.strftime("%Y/%m/%d %H:%M:%S %p").lower() for dt_str in dt_time_slots]

			return dt_str_time_slots


		except requests.exceptions.RequestException as e:
			print(f'Request failed: {e}')

		return None

class SetmoreCustomers:
	def __init__(self, auth):
		self.auth = auth

	def make_request(self, url, headers, method, json=None):
		""" Make a request
		``url (required, str)`` url
		``headers (required, str)`` headers in a json string
		``method (required, str)`` get or post
		``payload (optional, str)`` payload in a json string
		"""
		# Depending on the HTTP method (get, post, etc.), we may need to handle data differently.
		if method.lower() == 'get':
			request_func = requests.get
		elif method.lower() == 'post':
			request_func = requests.post

		if json is not None:
			response = request_func(url, headers=headers, json=json) #type: ignore

			if response.status_code == 401:
				# Unauthorized. Refresh the token and try again.
				self.auth.generate_access_token()
				headers['Authorization'] = f'Bearer {self.auth.access_token}'  # Update the headers with the new token.
				response = request_func(url, headers=headers, json=json) #type: ignore
		else:
			response = request_func(url, headers=headers) #type: ignore

			if response.status_code == 401:
				# Unauthorized. Refresh the token and try again.
				self.auth.generate_access_token()
				headers['Authorization'] = f'Bearer {self.auth.access_token}'  # Update the headers with the new token.
				response = request_func(url, headers=headers) #type: ignore
		return response

	def create_customer(self, customer_data):
		"""
		Create a customer in Setmore.

		:param customer_data: A dictionary containing customer data.
			Required fields:
				- first_name (str): The customer's first name.
			Optional fields:
				- last_name (str): The customer's last name.
				- email_id (str): The customer's email address.
				- country_code (str): The customer's country code.
				- cell_phone (str): The customer's cell phone number.
				- work_phone (str): The customer's work phone number.
				- home_phone (str): The customer's home phone number.
				- address (str): The customer's address.
				- city (str): The customer's city.
				- state (str): The customer's state.
				- postal_code (str): The customer's postal code.
				- image_url (str): The URL of the customer's image.
				- comment (str): Additional comment about the customer.
				- additional_fields (dict): Additional custom fields.
		:return: The customer ID if creation is successful, None otherwise.
		"""
		headers = {
			'Content-Type': 'application/json',
			'Authorization': f'Bearer {self.auth.access_token}'
		}

		try:
			response = self.make_request('https://developer.setmore.com/api/v1/bookingapi/customer/create', headers, 'post', json=customer_data)
			response.raise_for_status()
			data = response.json()
			customer_id = data.get('data', {}).get('customer', {}).get('key')
			return customer_id
		except requests.exceptions.RequestException as e:
			print(f'Request failed: {e}')
		
		return None

	def get_customer_details(self, firstname=None, email=None, phone=None):
		"""
		Retrieve customer details from Setmore.

		:param firstname: The customer's first name (required).
		:param email: The customer's email address.
		:param phone: The customer's phone number.
		:return: A list of customer details if retrieval is successful, None otherwise.
		"""
		headers = {
			'Content-Type': 'application/json',
			'Authorization': f'Bearer {self.auth.access_token}'
		}
		
		payload = {
			'firstname': firstname,
			'email': email,
			'phone': phone
		}

		try:
			response = self.make_request('https://developer.setmore.com/api/v1/bookingapi/customer', headers, 'get', json=payload)
			response.raise_for_status()
			data = response.json()
			customer_details = data.get('data', {}).get('customer')
			return customer_details
		except requests.exceptions.RequestException as e:
			print(f'Request failed: {e}')

		return None
	
class SetmoreAppointments:
	def __init__(self, auth):
		self.auth = auth
		self.make_request = self.make_request

	def make_request(self, url, headers, method, json=None):
		""" Make a request
		``url (required, str)`` url
		``headers (required, str)`` headers in a json string
		``method (required, str)`` get or post
		``payload (optional, str)`` payload in a json string
		"""
		# Depending on the HTTP method (get, post, etc.), we may need to handle data differently.
		if method.lower() == 'get':
			request_func = requests.get
		elif method.lower() == 'post':
			request_func = requests.post

		if json is not None:
			response = request_func(url, headers=headers, json=json) #type: ignore

			if response.status_code == 401:
				# Unauthorized. Refresh the token and try again.
				self.auth.generate_access_token()
				headers['Authorization'] = f'Bearer {self.auth.access_token}'  # Update the headers with the new token.
				response = request_func(url, headers=headers, json=json) #type: ignore
		else:
			response = request_func(url, headers=headers) #type: ignore

			if response.status_code == 401:
				# Unauthorized. Refresh the token and try again.
				self.auth.generate_access_token()
				headers['Authorization'] = f'Bearer {self.auth.access_token}'  # Update the headers with the new token.
				response = request_func(url, headers=headers) #type: ignore
		return response

	def create_appointment(self, appointment_data):
		headers = {
			'Content-Type': 'application/json',
			'Authorization': f'Bearer {self.auth.access_token}'
		}

		try:
			response = self.make_request('https://developer.setmore.com/api/v1/bookingapi/appointments', headers, 'post', json=appointment_data)
			response.raise_for_status()
			data = response.json()
			appointment_id = data.get('data', {}).get('appointment_id')
			return appointment_id
		except requests.exceptions.RequestException as e:
			print(f'Request failed: {e}')
		
		return None

##### note to self... this requires method put so all make_request() functions need to be updated to include functionality for put####
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
			response = self.make_request('https://developer.setmore.com/api/v1/bookingapi/appointments', headers, 'get')
			response.raise_for_status()
			data = response.json()
			appointments = data.get('data', [])
			return appointments
		except requests.exceptions.RequestException as e:
			print(f'Request failed: {e}')
		
		return None