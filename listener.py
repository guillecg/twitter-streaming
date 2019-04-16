import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from pymongo import MongoClient

import json
from utils.json_files import load_json


FORMAT_STD_OUT = lambda x, w=9: \
    '[{message: <{width}}]'.format(message=x, width=w)

KEYS = load_json('config/config.json')


class CustomListener(StreamListener):
    ''' A listener handles tweets that are received from the stream.
    This listener inserts the tweets in a mongoDB collection of tweets.
    '''

    def __init__(self, db, collection, hashtag_key, port=27017):
        # Stablish connection with MongoDB
        self.client = MongoClient('localhost', port)
        self.db = self.client[db]
        self.collection = self.db[collection]

        self.hashtag_key = hashtag_key.lower()


    def on_data(self, data):
        msg = json.loads(data)

        # Avoid tweets without the keyword as hashtag
        hashtags = msg['entities']['hashtags']
        if hashtags:
            hashtags = [tag.lower()
                        for tag_dict in hashtags
                        for tag in tag_dict.values()
                        if isinstance(tag, str)]

            if self.hashtag_key not in hashtags:
                return True

        # Avoid tweets without hashtag
        else:
            return True

        try:
            print(FORMAT_STD_OUT('EXT'), msg['extended_tweet']['full_text'])

        except KeyError:
            print(FORMAT_STD_OUT('MSG'), msg['text'])

        except BaseException as e:
            print(FORMAT_STD_OUT('ERROR'), e)
            return False

        finally:
            self.collection.insert(msg)
            return True


    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            print(FORMAT_STD_OUT('ERROR'), status_code)
            return False


# TODO: add sentiment analysis of a hashtag (e.g. Brexit)
# TODO: add sentiment analysis of a user (e.g. Theresa May): tweetL = api.user_timeline(screen_name='sdrumm', tweet_mode="extended")
# TODO: compare world vs UK
# TODO: color countries by median sentiment

# TODO: get full text

# TODO: get more accurate locations:
# https://stackoverflow.com/questions/31471447/tweepy-search-by-a-country-and-not-with-coordinates
# http://docs.tweepy.org/en/v3.5.0/api.html
# uk_location = [-6.38, 49.87, 1.77, 55.81] # from https://stackoverflow.com/questions/22889122/how-to-add-a-location-filter-to-tweepy-module


if __name__ == '__main__':
    auth = OAuthHandler(KEYS['consumer_key'], KEYS['consumer_secret'])
    auth.set_access_token(KEYS['access_token'], KEYS['access_secret'])
    api = tweepy.API(auth)
    print(FORMAT_STD_OUT('AUTH'), api.me().name)

    keyword = 'brexit'
    hashtag = '#' + keyword
    # hashtag_list = [hashtag.capitalize(), hashtag.lower(), hashtag.upper()]

    uk_location = [-12.0677673817, 49.9651490804, 1.785992384, 61.1291966094]
    world_location = [-180, -90, 180, 90]

    uk_listener = CustomListener(
        db='tweets',
        collection='uk_' + keyword,
        hashtag_key=keyword,
    )

    uk_stream = Stream(auth=auth, listener=uk_listener, tweet_mode='extended')
    uk_stream.filter(
        is_async=False,
        track=[hashtag],
        languages=['en'],
        locations=uk_location,
    )
