from logging import exception
import re
import tweepy
import json

def retweet_book(tweet_id) : 
    #api = twitter_authorization()

    #status = api.get_status(tweet_id)
    #if status.retweeted == True: #undo the previous retweet
    #    api.unretweet(tweet_id)    
    #api.retweet(tweet_id)

    #tweet = api.get_tweet(id=tweet_id)
    #print(tweet.data.text)  

    return

def tweet(text) :
    api, oldapi = twitter_authorization()

    #tweet
    result = api.create_tweet(text=text)
    #like it
    #tweet_id=result.data['id']
    #api.like(tweet_id=tweet_id)
    return

def tweet_with_media(text, image) :
    api, oldapi = twitter_authorization()
    #tweet
    media = oldapi.media_upload(filename=image)
    status = api.create_tweet(text=text, media_ids=[media.media_id])
    #like it
    #api.create_favorite(status.id)
    return

def twitter_authorization() :

    #twitter_secret_file = "secret/twitter-keys.json"
    #test account
    twitter_secret_file = "secret/twitter-keys2.json"

    with open(twitter_secret_file, "r") as file_hdl:
        keys = json.load(file_hdl)

    #v2
    api = tweepy.Client(
                        consumer_key=keys["key"],
                        consumer_secret=keys["secret"],
                        access_token=keys["accesstoken"],
                        access_token_secret=keys["accesstokensecret"])
    #v1 for load_media    
    auth = tweepy.OAuth1UserHandler(
                        consumer_key=keys["key"],
                        consumer_secret=keys["secret"],
                        access_token=keys["accesstoken"],
                        access_token_secret=keys["accesstokensecret"])
    oldapi = tweepy.API(auth)

    #api = tweepy.Client(bearer_token=keys["beartoken"])

    return(api, oldapi)

def tweet_quote(quote, author, tweet_id) :

    api, oldapi = twitter_authorization()

    if tweet_id:
        #retweet
        #status = api.get_status(tweet_id)
        #if status.retweeted == True: #undo the previous retweet
        #    api.unretweet(tweet_id)    
        #api.retweet(tweet_id)
        print("tweet_quote, tweet_id!=None")
    else:
        #hashtags = "#quote #quoteoftheday"
        tweet_text = quote +" " + "—" + author# + "  " + hashtags
        #tweet
        status = api.create_tweet(text=tweet_text)
        #like it
        #api.create_favorite(status.id)
    
    return


#tweet with media
#tweet_with_media("Elon Musk", "static/facts/elonquote-OLD.jpeg")

#tweet_quote("quote", "author", None)
#tweet("Hello Twitter")
#tweet("So please, oh please, we beg, we pray, go throw your TV set away, and in its place you can install a lovely bookshelf on the wall. -Roald Dahl")

