import re

import numpy as np

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
from sklearn import model_selection
from sklearn.pipeline import Pipeline

from textblob import TextBlob

from pymongo import MongoClient


# https://www.geeksforgeeks.org/twitter-sentiment-analysis-using-python/
# https://towardsdatascience.com/multinomial-naive-bayes-classifier-for-text-analysis-python-8dd6825ece67
# https://marcobonzanini.com/2015/05/17/mining-twitter-data-with-python-part-6-sentiment-analysis-basics/
# https://medium.freecodecamp.org/basic-data-analysis-on-twitter-with-python-251c2a85062e


class TextPreprocesser(object):
    def __init__(self):
        pass

    def clean_text(self, text):
        ''' Utility function to clean text by removing links, special
        characters using simple regex statements.
        '''
        return ' '.join(
            re.sub(
                '(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)', ' ', text
            ).split()
        )

    def get_sentiment(self, text):
        ''' Utility function to classify sentiment of passed text using
        textblob's sentiment method
        '''
        # Create TextBlob object of passed text
        analysis = TextBlob(self.clean_text(text))

        # Set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'


class BoWClassifier(TextPreprocesser):
    def __init__(self):
        pass


if __name__ == '__main__':
    client = MongoClient('localhost', port=27017)
    db = client['tweets']
    collection = db['uk_brexit']

    res = collection.find({}, {'_id' : False})
    res = list(res[:])[:10]

    clf = BoWClassifier()

    tweets = [clf.clean_text(tweet['text']) for tweet in res]
    sentiments = [clf.get_sentiment(tweet) for tweet in tweets]
