import tweepy as tweepy
from dotenv import load_dotenv
import six
import os
from string import punctuation
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk 
import re

def ensureUtf(s):
    try:
        if type(s) == unicode:
            return s.encode('utf8', 'ignore')
    except:
        return str(s)

class TwitterClient():

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.consumer_key = "Sc4rmZap7AeT8oab3ClS3EJrZ"
        self.consumer_secret = "Lzj3jyRgbisQEztuMEV4KYZEN2j88IK9llXMccI89bRqNEB8x9"
        self.access_token = "1211906574-4JX1Ur02Qd6fwmgvtl8aX7wHNFzHTDLde1TpcHU"
        self.access_token_secret = "j4OMr95yVHIki9Kt0AyZor8tq3i1tR72Zvpk0LebJlCgd"

        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    def get_tweet_texts(self, keyword):
        print(keyword)
        tweets = []
        for tweet in tweepy.Cursor(self.api.search, q=keyword).items(120):
            try:
                tweets.append(tweet.text)
            except tweepy.TweepError as error:
                print(error.reason)
            except StopIteration:
                break
        return tweets

class Utils:
    def __init__(self):
        pass

    def build_vocabulary(self, data):
        all_words = []
        for words in data: 
            all_words.extend(words)
        word_list = nltk.FreqDist(all_words).keys()
    
        return word_list

    def feature_extraction(self, data, word_features):
        tweet_words = set(data)
        features = {}
        for word in word_features:
            features['contains(%s)' % word] = (word in tweet_words)

        return features


class PreprocessingData:

    def __init__(self):
        self.stop_words = set(stopwords.words('english') + list(punctuation) + ['AT_USER', 'URL'])

    def process_tweet(self, tweets):
        for tweet in tweets:
            tweet = tweet.lower()
            tweet = re.sub('#', '', tweet)
            tweet = word_tokenize(tweet)
    
    def process_tweets(self, tweets):
        tweets = []
        for tweet in tweets:
            tweets.append(self.process_tweets(tweet["text"], tweet["label"]))
        return tweets

def main():

    project_folder = os.path.expanduser('~/machine-learning/01_sentimental_analyzer/prep')
    load_dotenv(os.path.join(project_folder, 'auth.env'))
    t = TwitterClient(os.environ.get('consumer_key'), os.environ.get('consumer_secret'), os.environ.get('access_token'), os.environ.get('access_token_secret'))
    tweets = t.get_tweet_texts('cricket')
    p = PreprocessingData()
    preprocessed = p.process_tweets(tweets)
    print('Starting to print preprocessed')
    for i in preprocessed:
        print(i)
    u = Utils()
    res = u.build_vocabulary(preprocessed)
    training_features = nltk.classify.apply_features(u.feature_extraction, preprocessed)
    NBayesClassifier = nltk.NaiveBayesClassifier.train(training_features)
    NBResultLabels = [NBayesClassifier.classify(u.feature_extraction(tweet[0])) for tweet in preprocessed]



if __name__ == '__main__':
    main()
