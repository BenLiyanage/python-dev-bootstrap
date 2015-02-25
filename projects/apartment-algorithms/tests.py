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
if __name__ == '__main__':
    unittest.main()