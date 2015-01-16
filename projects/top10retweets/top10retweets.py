from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
from urllib import quote,unquote
import pandas
from datetime import datetime, timedelta

# Please note, this script is inteded to be run inside of the django framework, as it leverages the database component for summations.

access_token = "29463499-9Og6hxW4HqFxcQyIrAdmLpbAnrwIk290ghOE0ez5f"
access_token_secret = "elXVYJRFmFFit3PiVTmI9eU0IvHqqD7H4yeEmClJ8c"
consumer_key = "8AqQCy7umStCyNN356v7fw"
consumer_secret = "vOvKV1QwuS1AeKPMIvJqErBxW7i1N12OL4UY2tNMs0c"

class twitterListener(StreamListener):
    
    
    def __init__(self, windowInMinutes):
        self.windowInMinutes = windowInMinutes
        self.retweets = pandas.DataFrame(columns=['text','date'])
        print self.retweets.columns.values
    def on_data(self, data):
        try:
            data = json.loads(data)
            
            if 'retweeted_status'  in data:
                # remove expiring records
                expireBefore = (datetime.now() - timedelta(minutes=self.windowInMinutes))
                
                self.retweets = self.retweets[self.retweets.date > expireBefore ]
                
                # add our new record
                self.retweets = self.retweets.append({'text':data['text'], 'date':datetime.now()}, ignore_index=True)
                
                top10 = self.retweets.groupby("text")["text"].agg(["count"]).sort('count',ascending=0).head(10)
                
                print '-----------------------------------------------'
                print '-----------------------------------------------'
                print '-----------------------------------------------'
                print '-----------------------------------------------'
                print top10
                
            return True
        except Exception as e:
            print "Error: " + str(e)

    def on_error(self, status):
        print status

# main function call
if __name__ == '__main__':
    
    #This handles Twitter authetification and the connection to Twitter Streaming API
    myListener = twitterListener(15)
    
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, myListener)
    stream.url = '/1.1/statuses/sample.json'
    stream.host = 'stream.twitter.com'
    stream.session.headers['Content-type'] = "application/x-www-form-urlencoded"
    stream.session.params = {'delimited': 'length'}
    stream._start(False)
    