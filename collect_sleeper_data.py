import requests
import json

#  TODO:
#     create functions to get more details besides counts for the different transactions
BASE_USER_URL = 'https://api.sleeper.app/v1/user/'
BASE_LEAGUE_URL = 'https://api.sleeper.app/v1/league/'

class User(object):
	"""Represents a user on Sleeper."""

	def __init__(self, user_info):
		self.id = user_info['user_id']
		self.name = user_info['username']
		self.leagues = self._get_leagues(self.id)

	def _get_leagues(self, id, year=2019):
		leagues = []
		leagues_response = requests.get(
			f'{BASE_USER_URL}{id}/leagues/nfl/{year}'
		)
		if leagues_response.status_code == 200:
			leagues = json.loads(leagues_response.text)
		return [League(league) for league in leagues]


class League(object):
	"""Represents a league on Sleeper."""

	def __init__(self, league_info):
		self.id = league_info['league_id']
		self.name = league_info['name']
		self.size = league_info['total_rosters']
		self.season = league_info['season']
		self.status = league_info['status']
		self.settings = league_info['settings']
		self.scoring_settings = league_info['scoring_settings']
		self.teams = self._get_teams()
		self.transactions = self._get_transactions()
		self.trades = self._get_transaction_type('trade')
		self.waivers = self._get_transaction_type('waiver')
		self.free_agents = self._get_transaction_type('free_agent')
		self._add_transaction_counts_to_teams()

	def _get_teams(self):
		teams = []
		managers = []
		rosters = []
		managers_response = requests.get(
			f'{BASE_LEAGUE_URL}{self.id}/users'
		)
		rosters_response = requests.get(
			f'{BASE_LEAGUE_URL}{self.id}/rosters'
		)
		if managers_response.status_code == 200:
			managers = json.loads(managers_response.text)
		if rosters_response.status_code == 200:
			rosters = json.loads(rosters_response.text)
		for manager in managers:
			user_id = manager['user_id']
			for roster in rosters:
				if roster['owner_id'] == user_id:
					teams.append(Team(manager, roster))
		return teams

	def _get_transactions(self):
		"""Gets all transactions for a league."""
		transactions = []
		for index in range(1, 17):
			transactions_response = requests.get(
				f'{BASE_LEAGUE_URL}{self.id}/transactions/{index}'
			)
			transactions += json.loads(transactions_response.text)
		return transactions

	def _add_transaction_counts_to_teams(self):
		for type in ['trade', 'waiver', 'free_agent']:
			transaction_type = getattr(self, f'{type}s')
			for transaction in transaction_type:
				transaction_participants = transaction['roster_ids']
				for team in self.teams:
					if team.roster_id in transaction_participants:
						transaction_count = getattr(team, f'{type}_count')
						setattr(team, f'{type}_count', transaction_count + 1)

	def _get_transaction_type(self, type):
		# Get a list of all transactions of the passed in type.
		transactions_of_type = []
		for transaction in self.transactions:
			if transaction['type'] == type:
				transactions_of_type.append(transaction)
		return transactions_of_type

	def display_counts(self):
		display = ''
		for team in self.teams:
			display += team.display_counts()
		print(display)


class Team(object):
	"""Represents a team within a league on Sleeper."""

	def __init__(self, manager_info, roster_info):
		self.user_id = manager_info['user_id']
		self.display_name = manager_info['display_name']
		# If a user has not set a team_name then the attribute is missing
		# entirely from the get request.
		try:
			self.team_name = manager_info['metadata']['team_name']
		except KeyError:
			self.team_name = ''
		self.roster_id = roster_info['roster_id']
		self.roster = roster_info['players']
		self.waiver_count = 0
		self.trade_count = 0
		self.free_agent_count = 0
		self._manager_info = manager_info
		self._roster_info = roster_info

	def display_counts(self):
		return (
			f'{self.display_name}: Trades: {self.trade_count}, Waivers: '
			f'{self.waiver_count}, Free Agents: {self.free_agent_count} \n'
		)
