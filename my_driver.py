import requests
import json

from collect_sleeper_data import User

BASE_USER_URL = 'https://api.sleeper.app/v1/user/'

#TODO fix this function and decide whether or not to move it elsewhere.
def get_user_info():
	valid_name = False
	while valid_name is False:
		username = input('Please enter your sleeper username: ')
		user_info = requests.get(f'{BASE_USER_URL}{username}')
		if user_info.status_code != 200:
			print('No user was found with that username, please try again.\n')
		else:
			valid_name = True
	return json.loads(user_info.text)

user_info = get_user_info()
user = User(user_info)
breakpoint()
