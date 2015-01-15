from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
from urllib import quote,unquote

access_token = "29463499-9Og6hxW4HqFxcQyIrAdmLpbAnrwIk290ghOE0ez5f"
access_token_secret = "elXVYJRFmFFit3PiVTmI9eU0IvHqqD7H4yeEmClJ8c"
consumer_key = "8AqQCy7umStCyNN356v7fw"
consumer_secret = "vOvKV1QwuS1AeKPMIvJqErBxW7i1N12OL4UY2tNMs0c"

class twitterListener(StreamListener):
    
    retweets = {}
    
    def on_data(self, data):
        try:
            data = json.loads(data)
            
            if 'retweeted_status' in data:
                ##store the tweet in a dictionary, with the text as the keys
                
                # I do this to handle international characters, that can't be in a dictionary
                key = quote(data['text'])
                if key in self.retweets:
                    self.retweets[key] += 1
                else:
                    self.retweets[key] = 1
                
                #convert the list to a sorted array
                #this is expensive, I'm being lazy.
                sortedRetweetKeys = sorted(self.retweets, key=self.retweets.get, reverse=True)
                
                #print the top 10
                tweetsToPrint = len(self.retweets)
                if tweetsToPrint > 10:
                    tweetsToPrint = 10
                
                print '-----------------------------------------------'
                print '-----------------------------------------------'
                print '-----------------------------------------------'
                print '-----------------------------------------------'
                for index in range(0,tweetsToPrint):
                    #unquote is to decode the text for international characters
                    print str(self.retweets[sortedRetweetKeys[index]]) + '-' + unquote(sortedRetweetKeys[index])
                    
                #exit()
        except Exception as e:
            print "Error: " + str(e)
            
        return True

    def on_error(self, status):
        print status

if __name__ == '__main__':

    #This handles Twitter authetification and the connection to Twitter Streaming API
    myListener = twitterListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, myListener)
    stream.url = '/1.1/statuses/sample.json'
    stream.host = 'stream.twitter.com'
    stream.session.headers['Content-type'] = "application/x-www-form-urlencoded"
    stream.session.params = {'delimited': 'length'}
    stream._start(False)
    