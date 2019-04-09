
import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import json
from pymongo import MongoClient

def load_json(json_path):
    '''Loads JSON files as a dictionary.
    '''
    with open(json_path, 'r', encoding='utf8') as json_file:
        json_dict = json.load(json_file)

    return json_dict


keys = load_json('config/config.json')


class CustomListener(StreamListener):
    ''' A listener handles tweets that are received from the stream.
    This listener inserts the tweets in a mongoDB collection of tweets.
    '''

    def on_data(self, data):
        try:
            msg = json.loads(data)

            print(msg['text'])

            client = MongoClient('localhost', 27017)
            db = client['Tweets']
            collection = db['Trump']
            collection.insert(msg)

            return True

        except BaseException as e:
            print('Error on_data: %s' % str(e))

    def on_error(self, status):
        print(status)


if __name__ == '__main__':
    auth = OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
    auth.set_access_token(keys['access_token'], keys['access_secret'])
    api = tweepy.API(auth)
    print('[AUTH]', api.me().name)

    listener = CustomListener()

    stream = Stream(auth, listener)
    stream.filter(track=['brexit'])
