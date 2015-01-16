import unittest
from top10retweets import twitterListener
import time

class listenerTester(unittest.TestCase):

    def test_on_data(self):
        myListener = twitterListener(15)
        
        with open('retweet.json', 'r') as file:
            json1 = file.read()
            
        with open('retweet2.json', 'r') as file:
            json2 = file.read()
        
        myListener.on_data(json1)
        myListener.on_data(json2)
        myListener.on_data(json2)
        myListener.on_data(json1)
        myListener.on_data(json1)
        
    def test_rolling_window(self):
        myListener = twitterListener(1)
        
        with open('retweet.json', 'r') as file:
            json1 = file.read()
        
        myListener.on_data(json1)
        
        time.sleep(70)
        myListener.on_data(json1)
        
        
if __name__ == '__main__':
    unittest.main()
