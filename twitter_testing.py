import re 
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob 
from objbrowser import browse
from pprint import pprint
import datetime

rounding = 4
  
class TwitterClient(object): 
    ''' 
    Generic Twitter Class for sentiment analysis. 
    '''
    def __init__(self): 
        ''' 
        Class constructor or initialization method. 
        '''
        # keys and tokens from the Twitter Dev Console 
        consumer_key = 'Ih2mlq5lsnqc9GEmgrkcoz8wj'
        consumer_secret = 'gr7tMB0QHlwqrL5f28YfzT5IDKsbRc9jyyqTIg0eRCrl29AzCJ'
        access_token = '827931206037622784-0AqKtYFM5DHvUySgxkJC3sGzwkSnWDs'
        access_token_secret = 'Ci8DJpBoRpuiggy2y7gamvctR1IjMGAOcgq5nfoB4FoRi'
  
        # attempt authentication 
        try: 
            # create OAuthHandler object 
            self.auth = OAuthHandler(consumer_key, consumer_secret) 
            # set access token and secret 
            self.auth.set_access_token(access_token, access_token_secret) 
            # create tweepy API object to fetch tweets 
            self.api = tweepy.API(self.auth) 
        except: 
            print("Error: Authentication Failed") 
  
    def clean_tweet(self, tweet): 
        ''' 
        Utility function to clean tweet text by removing links, special characters 
        using simple regex statements. 
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split()) 
  
    def get_tweet_sentiment(self, tweet): 
        ''' 
        Utility function to classify sentiment of passed tweet 
        using textblob's sentiment method 
        '''
        # create TextBlob object of passed tweet text 
        analysis = TextBlob(self.clean_tweet(tweet)) 
        # set sentiment 
        if analysis.sentiment.polarity > 0: 
            return 'positive'
        elif analysis.sentiment.polarity == 0: 
            return 'neutral'
        else: 
            return 'negative'
  
    def get_tweets(self, query, count = 10): 
        ''' 
        Main function to fetch tweets and parse them. 
        '''
        # empty list to store parsed tweets 
        tweets = [] 
  
        try: 
            # call twitter api to fetch tweets 
            fetched_tweets = self.api.search(q = query, count = count) 
  
            # parsing tweets one by one 
            for tweet in fetched_tweets: 
                # empty dictionary to store required params of a tweet 
                parsed_tweet = {} 
  
                # saving text of tweet 
                parsed_tweet['text'] = tweet.text 
                # saving sentiment of tweet 
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)
                parsed_tweet['created'] = tweet.created_at
  
                # appending parsed tweet to tweets list 
                if tweet.retweet_count > 0: 
                    # if tweet has retweets, ensure that it is appended only once 
                    if parsed_tweet not in tweets: 
                        tweets.append(parsed_tweet) 
                else: 
                    tweets.append(parsed_tweet) 
  
            # return parsed tweets 
            return tweets
  
        except tweepy.TweepError as e: 
            # print error (if any) 
            print("Error : " + str(e)) 
  
def main(): 
    # creating object of TwitterClient Class 
    api = TwitterClient() 
    # calling function to get tweets 
    tweets = api.get_tweets(query = 'Bitcoin', count = 10000)
    #browse(locals())
    #print(dir(fetched_tweets))
    
    # picking positive tweets from tweets 
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive'] 

    # percentage of positive tweets 
    print(f"Positive tweets percentage: {round(100*len(ptweets)/len(tweets), rounding)} %")

    # picking negative tweets from tweets 
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative'] 

    # percentage of negative tweets 
    print(f"Negative tweets percentage: {round(100*len(ntweets)/len(tweets), rounding)} %") 

    # percentage of neutral tweets 
    print(f"Neutral tweets percentage: {round(100*(len(tweets) - len(ntweets) - len(ptweets))/len(tweets), rounding)} %")
  
    # printing first 5 positive tweets 
    print("\n\nPositive tweets:") 
    for tweet in ptweets[:5]: 
        print(tweet['text']) 
  
    # printing first 5 negative tweets 
    print("\n\nNegative tweets:") 
    for tweet in ntweets[:5]: 
        print(tweet['text']) 
    
if __name__ == "__main__": 
    # calling main function 
    #main()
    client = TwitterClient()

    #tweets = client.api.search(q = "Bitcoin", count = 1000)
    tweets = client.get_tweets(query = "Bitcoin", count = 1000)
    print(tweets[0])

    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(1)

    print(type(yesterday))

    '''
    if tweets[0]['created'] > datetime.datetime.now():
        print(f"Datetime older is greater")
    else:
        print("Datetime younger is greater")
    '''
    #pprint(type(tweets[0]))
    #pprint(len(tweets[0]))
    #pprint(dir(tweets[0]))
    #pprint(tweets[0].__dict__['created_at'])