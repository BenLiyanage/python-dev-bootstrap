import unittest
from exercise_leasing_agent_leaderboards import LeaderBoard

class Tests(unittest.TestCase):

	def test_get_market_rent(self):
		myLeaderBoard = LeaderBoard()
		self.assertEqual(myLeaderBoard.get_market_rent('407-5-B1'), 475)
		
	def test_rent_increase(self):
		myLeaderBoard = LeaderBoard()
		self.assertEqual(myLeaderBoard.rent_increase(475, 476), 1)
	
	def test_rent_lost(self):
		myLeaderBoard = LeaderBoard()
		self.assertEqual(myLeaderBoard.rent_lost(30, 1), 1)
		self.assertEqual(myLeaderBoard.rent_lost(15, 2), 1)
		
	def test_quarter_from_datestamp(self):
		myLeaderBoard = LeaderBoard()
		self.assertEqual(myLeaderBoard.quarter_from_datestamp('2015-01-01'), 1)
		self.assertEqual(myLeaderBoard.quarter_from_datestamp('2015-03-01'), 1)
		self.assertEqual(myLeaderBoard.quarter_from_datestamp('2015-04-01'), 2)
		self.assertEqual(myLeaderBoard.quarter_from_datestamp('2015-12-01'), 4)
	
	def test_listing_cost(self):
		myLeaderBoard = LeaderBoard()
		
		self.assertEqual(myLeaderBoard.listing_cost('Apartment Guide', '2015-12-01'), 0)
		self.assertEqual(myLeaderBoard.listing_cost('Apartments.com', None), 0)
		self.assertEqual(myLeaderBoard.listing_cost('Apartments.com', '2015-12-01'), 295)
	
if __name__ == '__main__':
    unittest.main()