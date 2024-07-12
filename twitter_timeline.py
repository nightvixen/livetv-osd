#!/usr/bin/env  python
# encoding: UTF-8
# sudo pip install tweepy
# http://tweepy.readthedocs.org/en/v3.2.0/getting_started.html#hello-tweepy
# Apps management: https://apps.twitter.com

import tweepy
from threading import Lock


#replace with your own keys
consumer_key = ''
consumer_secret = ''

access_token = ''
access_token_secret = ''

twitter_enable = False
twiobj_lock = Lock()
tweets_obj = []
tweets_bandict = {}

if twitter_enable == True:
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)


def go():
    global twitter_enable, tweets_obj, twiobj_lock, tweets_bandict

    if twitter_enable == False:
        return "** Twitter line is disabled, please enable it in config **"
    tweets = []
    tweetobj_tmp = []

    twiobj_lock.acquire()
    try:
        for i in api.search("FUCK", count=20, result_type='mixed'):
            tweet =  "@" + i.user.screen_name + ': ' + i.text
            # filtering
            if (tweets_bandict.get(i.id) == None):
                tweets.append(tweet)
                tweetobj_tmp.append({"id": i.id, "text": i.text})
            else:
                tweetobj_tmp.append({"id": i.id, "text": i.text, "banned": True})

    finally:
        tweets_obj = tweetobj_tmp
        twiobj_lock.release()


    return ' ** '. join(tweets)

def getTweets():
    return tweets_obj

def banTwi(twiId):
    global tweets_bandict, twiobj_lock, tweets_obj

    twiobj_lock.acquire()

    try:
        tweets_bandict.update({twiId: True})
        for tw in tweets_obj:
            if (tw['id'] == twiId):
                tw.update({"banned": True})
    finally:
        twiobj_lock.release()

    return "OK"

if __name__ == "__main__":
    print go()
