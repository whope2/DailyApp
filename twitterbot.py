import tweepy
import json

def retweet_book(tweet_id) : 
    api = twitter_authorization()

    status = api.get_status(tweet_id)
    if status.retweeted == True: #undo the previous retweet
        api.unretweet(tweet_id)    
    api.retweet(tweet_id)
    return

def twitter_authorization() :

    twitter_secret_file = "secret/twitter-keys.json"

    with open(twitter_secret_file, "r") as file_hdl:
        keys = json.load(file_hdl)

    auth = tweepy.OAuthHandler(keys["key"], keys["secret"])
    auth.set_access_token(keys["accesstoken"], keys["accesstokensecret"])

    api = tweepy.API(auth)
    user = api.get_user("tothemax2050")
    print(user.name)
    print(user.description)
    
    return(api)

def tweet_quote(quote, author, tweet_id) :

    api = twitter_authorization()

    if tweet_id:
        #retweet
        status = api.get_status(tweet_id)
        if status.retweeted == True: #undo the previous retweet
            api.unretweet(tweet_id)    
        api.retweet(tweet_id)
    else:
        hashtags = "#quote #quoteoftheday"
        tweet_text = quote +"\n" + "—" + author + "  " + hashtags
        #tweet
        status = api.update_status(tweet_text)
        #like it
        api.create_favorite(status.id)
    
    return

'''
status = api.get_status(1399404140414046210)

user = api.get_user("tothemax2050")
print(user.name)
print(user.description)
print(user.followers)
print(user.location)

for tweet in api.search(q="quoteoftheday", lang="en"):
    print(tweet.text)

'''
#test
#gates_tweet_id = 1404841704507674629
#my_tweet_id = 1402663278036369409
#retweet_book(my_tweet_id)
