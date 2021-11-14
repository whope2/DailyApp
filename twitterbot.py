from logging import exception
import re
import tweepy
import json

def retweet_book(tweet_id) : 
    api = twitter_authorization()

    status = api.get_status(tweet_id)
    if status.retweeted == True: #undo the previous retweet
        api.unretweet(tweet_id)    
    api.retweet(tweet_id)
    return

def get_my_followers() : 
    api = twitter_authorization()
    me = api.get_user("tothemax2050")
    number_of_followers=me.followers_count
    print(number_of_followers)
    follower_list = []
    followers = tweepy.Cursor(api.followers_ids, user_id=me.id, tweet_mode="extended").items()
    for i in range(0,number_of_followers):
        try:
            user=next(followers)
            #user_status = api.get_user(user)
            #print(user)
            follower_list.append(user)
        except StopIteration:
            break
    #print(i)
    return follower_list

def like_goodreads_replies(tweet_id, num):
    api = twitter_authorization()
    name = 'goodreads'
    count = 0
    exception_count = 0
    replies=[]
    authorlist = []
    my_follower_list = get_my_followers()
    for tweet in tweepy.Cursor(api.search,q='to:'+name, result_type='recent').items(num):
        if hasattr(tweet, 'in_reply_to_status_id_str'):
            if (tweet.in_reply_to_status_id_str==tweet_id):
                replies.append(tweet)
    for tweet in replies:
        status = api.get_status(tweet.id) #Call api.get_status so status.favorited is correct
        if((status.favorited == False) and (status.author.id not in authorlist) and (status.author.id not in my_follower_list)):
            try: 
                print("tweet.id = %s, tweet.text = %s" % (tweet.id,status.text))
                api.create_favorite(status.id)
                authorlist.append(status.author.id)
                count += 1
            except Exception as e:
                exception_count += 1
                print("like_replies create_favorite exception: %s" % e)
    print("num=%d, count = %s, exception_count = %s" %(num, count, exception_count))
    return count, exception_count

def get_likes(tweet_id) : 
    api = twitter_authorization()
    status = api.get_status(tweet_id)
    like_count = status.favorite_count + status.retweet_count
    return like_count

def like_tweets(hashtag, num) : 
    api = twitter_authorization()
    tweets = tweepy.Cursor(api.search, hashtag, lang="en",tweet_mode='extended').items(3*num)
    attempt_count = 0 
    count = 0
    exception_count = 0
    authorlist = []
    my_follower_list = get_my_followers()
    for tweet in tweets:
        if(count>=num):
            break
        attempt_count += 1
        status = api.get_status(tweet.id)
        if((status.favorited == False) and (status.author.id not in authorlist) and (status.author.id not in my_follower_list)):
            try: 
                api.create_favorite(tweet.id)
                authorlist.append(status.author.id)
                count += 1
                print(".")
            except Exception as e:
                exception_count += 1
                print("like_tweets create_favorite exception: %s" % e)
    print("like tweets: hashtag=%s, num=%d, attempt=%d, count=%d, execption_count=%d" % (hashtag,num,attempt_count,count,exception_count))
    return attempt_count, count, exception_count

def twitter_authorization() :

    twitter_secret_file = "secret/twitter-keys.json"

    with open(twitter_secret_file, "r") as file_hdl:
        keys = json.load(file_hdl)

    auth = tweepy.OAuthHandler(keys["key"], keys["secret"])
    auth.set_access_token(keys["accesstoken"], keys["accesstokensecret"])

    api = tweepy.API(auth)
    #user = api.get_user("tothemax2050")
    #print(user.name)
    #print(user.description)
    
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

#like_tweets("#ebook", 30)
#like_tweets("#bookrecommendations", 10)
#like_tweets("#booklovers", 10)
#like_tweets("#reading", 10)
#like_tweets("#goodreadswithaview", 10)

#get_my_followers()

#count, exception_count = like_goodreads_replies("1456629378876596229", 100)
#print("count=%s, exception_count=%s" % (count,exception_count))
