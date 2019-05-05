import re

import numpy as np
import pandas as pd

from collections import Counter, defaultdict

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
from sklearn import model_selection
from sklearn.pipeline import Pipeline

from textblob import TextBlob

from pymongo import MongoClient

import matplotlib.pyplot as plt

import seaborn as sns
sns.set(style='white')

from stop_words import get_stop_words
from nltk.corpus import stopwords
from wordcloud import WordCloud, STOPWORDS

# https://www.geeksforgeeks.org/twitter-sentiment-analysis-using-python/
# https://towardsdatascience.com/multinomial-naive-bayes-classifier-for-text-analysis-python-8dd6825ece67
# https://marcobonzanini.com/2015/05/17/mining-twitter-data-with-python-part-6-sentiment-analysis-basics/
# https://medium.freecodecamp.org/basic-data-analysis-on-twitter-with-python-251c2a85062e
# https://datascienceplus.com/twitter-analysis-with-python/
# https://medium.com/analytics-vidhya/simplifying-social-media-sentiment-analysis-using-vader-in-python-f9e6ec6fc52f


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


class SentimentAnalyser(TextPreprocesser):
    def __init__(self):
        pass

    def get_sentiment(self, text):
        ''' Utility function to classify sentiment of passed text using
        textblob's sentiment method
        '''
        # Create TextBlob object of passed text
        analysis = TextBlob(self.clean_text(text))

        return analysis.sentiment.polarity


def plot_wordcloud(text):

    # Generate a word cloud image
    wordcloud = WordCloud(
        width=1600, height=1200
    ).generate(' '.join(text))
    plt.figure(figsize=(20,10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')

    # lower max_font_size
    # wordcloud = WordCloud(
    #     width=800, height=400, max_font_size=50
    # ).generate(' '.join(text))
    # plt.figure(figsize=(20,10))
    # plt.imshow(wordcloud, interpolation='bilinear')
    # plt.axis('off')

    # Show the plots
    plt.show()


REGION = 'eu'


if __name__ == '__main__':
    client = MongoClient('localhost', port=27017)
    db = client['tweets']
    collection = db['{}_brexit'.format(REGION)]

    res = collection.find({}, {'_id': False})
    res = list(res[:])

    analyser = SentimentAnalyser()
    clean_tweets = [analyser.clean_text(tweet['text']) for tweet in res]
    sentiments = {
        res[idx]['created_at']: analyser.get_sentiment(tweet)
        for idx, tweet in enumerate(clean_tweets)
    }

    sentiments_per_day = defaultdict(list)
    sentiments_categorical = dict()
    for key, value in sentiments.items():
        key_formatted = '-'.join(key.split(' ')[1:3])
        sentiments_per_day[key_formatted].append(value)

        if value > 0:
            categorical_value = 'positive'
        elif value == 0:
            categorical_value = 'neutral'
        else:
            categorical_value = 'negative'

        sentiments_categorical[key] = categorical_value

    sentiments_counter = Counter(sentiments_categorical.values())

    # Sort keys for the barplot palette
    key_order = ['positive', 'neutral', 'negative']
    sentiments_counter = {k: sentiments_counter[k] for k in key_order}

    # Sentiment plots
    sentiments_count_df = pd.DataFrame({
        'Sentiment': list(sentiments_counter.keys()),
        'Count': list(sentiments_counter.values()),
    })
    ax = sns.barplot(
        x='Sentiment', y='Count', data=sentiments_count_df, palette='RdBu_r'
    )

    sentiments_per_day_long = [
        (key, value)
        for key, value_list in sentiments_per_day.items()
        for value in value_list
    ]
    sentiments_dates_long_df = pd.DataFrame({
        'Dates': list(map(lambda x: x[0], sentiments_per_day_long)),
        'Sentiment': list(map(lambda x: x[1], sentiments_per_day_long))
    })

    ax = sns.scatterplot(
        x='Dates', y='Sentiment', data=sentiments_dates_long_df,
        hue='Sentiment', palette='RdBu_r'
    )
    plt.show()

    ax = sns.pointplot(
        x='Dates', y='Sentiment', data=sentiments_dates_long_df,
        palette='viridis'
    )
    plt.show()

    ax = sns.boxplot(
        x='Dates', y='Sentiment', data=sentiments_dates_long_df,
        palette='viridis'
    )
    plt.show()


    # Wordcloud

    stop_words = list(get_stop_words('en'))       # About 900 stopwords
    nltk_words = list(stopwords.words('english')) # About 150 stopwords
    custom_words = ['brexit', 'eu', 'uk', 'rt']
    final_stop_words = stop_words + nltk_words + custom_words

    final_tweets = []
    for sentence in clean_tweets:
        final_tweets.extend(sentence.split())

    final_tweets = [w for w in final_tweets
                    if w.lower() not in final_stop_words]

    plot_wordcloud(final_tweets)
