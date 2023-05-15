import requests
import json
import os
import datetime

class SetmoreTimeSlots:
	def __init__(self, auth):
		self.auth = auth

	def get_slots(self, staff_key=None, service_key=None, selected_date=None, off_hours=False, double_booking=False, slot_limit=None, timezone=None):
		"""
		Get all available time slots for the given service, staff, and date.

		Args:
			:param staff_key (str, required): The staff key for filtering time slots. Default is None.
			:param service_key (str, required): The service key for filtering time slots. Default is None.
			:param selected_date (str, required): The selected date in the format "DD/MM/YYYY". Default is today.
			:param off_hours (bool, optional): Flag to include off-hours time slots. Default is False.
			:param double_booking (bool, optional): Flag to allow double booking. Default is False.
			:param slot_limit (int, optional): Maximum number of time slots to retrieve. Default is None (no limit).
			:param timezone (str, optional): Timezone for the returned time slots. Default's to your company's timezone or None if not available.

		Returns:
			list or str: List of available time slots in the format ["HH.MM", "HH.MM", ...], or a string indicating no available time slots.

		Raises:
			ValueError: If the response format is invalid.
			ValueError: If the request fails with an error status code.

		Raises a ValueError if the response format is invalid, indicating a problem with the API response structure.
		Raises a ValueError if the request fails with an error status code, providing the error message from the API response.

		Example:
			sm = SetmoreApi()
			slots = sm.get_slots(staff_key="XXXXXXXX", service_key="XXXXXXX", selected_date="DD/MM/YYYY", off_hours=True, double_booking=True, slot_limit=30, timezone="America/Los_Angeles")
			if isinstance(slots, list):
				for slot in slots:
					print(slot)
			else:
				print(slots)
			"""
		if selected_date is None or selected_date == '':
			selected_date = datetime.date.today().strftime("%d/%m/%Y")
			print(selected_date)
		required_params = ['staff_key', 'service_key', 'selected_date']
		missing_params = [param for param in required_params if locals().get(param) is None]


		if missing_params:
			raise Exception(f'Missing required parameters: {", ".join(missing_params)}')
		
		try:
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
					print(data)
					print(type(data))
			else:
				error_message = f'Request failed with status code {response.status_code}: {response.text}'
				raise ValueError(error_message)
		except requests.exceptions.RequestException as e:
			# Request exception occurred
			raise Exception(f'Request exception occurred: {str(e)}')