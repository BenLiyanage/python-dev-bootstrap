=Overview=

Use Twitter's sample streaming API to show the top 10 retweeted tweets (note the retweeted_status field) in a rolling window of time, where the window's start is n minutes ago (where n is defined by the user) and the window's end is the current time.

Output should continuously update and include the tweet text and number of times retweeted in the current rolling window. You should not use the retweet_count field, but instead count the retweets that your program actually processes.