import json
import pandas
from datetime import datetime
import numpy

class LeaderBoard():
	def closing_time(self, first_seen, lease_signed):
		format = "%Y-%m-%d"
		delta = datetime.strptime(lease_signed, format) - datetime.strptime(first_seen, format)
		return delta.days

	def get_market_rent(self, name):
		unit = self.unit_market_rents
		unit = unit.loc[self.unit_market_rents['name']==name]
		if len(unit) > 1:
			unit = unit.sort('datestamp')
			
		return unit.iloc[0]['market_rent']
		
	def __init__(self):
		with open('guest_cards.json', 'r') as file:
			self.guest_cards = pandas.DataFrame(json.loads(file.read()))

		with open('unit_market_rents.json', 'r') as file:
			self.unit_market_rents = pandas.DataFrame(json.loads(file.read()))
	
	def rent_increase(self, market_rent, resident_rent):
		return resident_rent - market_rent
		
	def rent_lost(self, closing_time, market_rent):
		#prorate based on a 30 day month
		return float(closing_time) / 30  * market_rent
	
	def future_rent_delta(self, rent_increase):
		return 12 * rent_increase
	
		
	def print_leader_board(self):
		signed = self.guest_cards[pandas.notnull(self.guest_cards['lease_signed'])]
		signed['market_rent'] = map(self.get_market_rent, signed['unit_name'])
		signed['closing_time'] = map(self.closing_time, signed['first_seen'], signed['lease_signed'])
		signed['rent_increase'] = map(self.rent_increase, signed['market_rent'], signed['resident_rent'])
		signed['rent_lost'] = map(self.rent_lost, signed['closing_time'], signed['market_rent'])
		signed['future_rent_delta'] = map(self.future_rent_delta, signed['rent_increase'])
		signed['net_profit'] = map(lambda rent_lost, future_rent_delta: rent_lost - future_rent_delta, signed['rent_lost'], signed['future_rent_delta'])
		signed['month'] = map(lambda lease_signed: lease_signed[0:7], signed['lease_signed'])
		
		leaderboard = signed.groupby(['month', 'agent_id']).sum()['net_profit'].reset_index()

		month = ''
		monthCount = 0
		
		for i in range(0, len(leaderboard)):
			
			if month != leaderboard.loc[i]['month']:
				monthCount = 1
				month = leaderboard.loc[i]['month']
				print month
			else:
				monthCount+=1
			
			if monthCount > 3:
				continue
			else:
				print "Let's pretend this is a name: " + str(leaderboard.loc[i]['agent_id'])
		
if __name__ == '__main__':
	myLeaderBoard = LeaderBoard()
	myLeaderBoard.print_leader_board()
# print guest_cards['lease_signed']






