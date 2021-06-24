import random
from elasticsearch import Elasticsearch
client = Elasticsearch()
'''
import requests

def stat_indices() :
    resp_indices = requests.get('http://localhost:9200/_cat/indices')
    return(resp_indices.content)

def stat_wordlist() :
    resp_wordlist = requests.get('http://localhost:9200/wordlist/_search?pretty')
    return(resp_wordlist.json())

def stat_quotelist() :
    resp_wordlist = requests.get('http://localhost:9200/quotelist/_search?pretty')
    return(resp_wordlist.json())

def stat_photolist() :
    resp_wordlist = requests.get('http://localhost:9200/photolist/_search?pretty')
    return(resp_wordlist.json())
'''

def get_a_random_word() :
    index_name = "wordlist"
    docs_count = client.count(index=index_name)['count']
    print("docs_count = %d" % docs_count)
    random_doc_id = random.randint(1,docs_count)
    print("generate random doc_id = %d" % random_doc_id)
    doc = client.get(index=index_name, id=str(random_doc_id))
    return(doc["_source"])

def get_a_random_quote() :
    index_name = "quotelist"
    docs_count = client.count(index=index_name)['count']
    print("docs_count = %d" % docs_count)
    random_doc_id = random.randint(1,docs_count)
    print("generate random doc_id = %d" % random_doc_id)
    doc = client.get(index=index_name, id=str(random_doc_id))
    return(doc["_source"]["Quote"] + " - " + doc["_source"]["Author"])

def get_a_random_quote_and_author() :
    index_name = "quotelist"
    docs_count = client.count(index=index_name)['count']
    random_doc_id = random.randint(1,docs_count)
    doc = client.get(index=index_name, id=str(random_doc_id))
    return(doc["_source"]["Quote"], doc["_source"]["Author"])

def get_a_random_love_quote() :
    index_name = "lovequotelist"
    docs_count = client.count(index=index_name)['count']
    print("docs_count = %d" % docs_count)
    random_doc_id = random.randint(1,docs_count)
    print("generate random doc_id = %d" % random_doc_id)
    doc = client.get(index=index_name, id=str(random_doc_id))
    print(doc)
    return(doc["_source"]["Quote"])

def get_a_random_photo() :
    index_name = "photolist"
    docs_count = client.count(index=index_name)['count']
    print("docs_count = %d" % docs_count)
    random_doc_id = random.randint(1,docs_count)
    print("generate random doc_id = %d" % random_doc_id)
    doc = client.get(index=index_name, id=str(random_doc_id))
    print(doc)
    return(doc["_source"]["Photo File Name"], doc["_source"]["Media ID"], doc["_source"]["Image URL"])

def get_a_random_book_tweet_id() :
    index_name = "booklist"
    #results=client.search(index=index_name, body={"query": { "exists": { "field": "TweetID"} } })
    results=client.search(index=index_name, body=\
        {
            "size":999,
            "query": {
                
                "bool": {
                    "should": [{
                        "exists": {
                            "field": "TweetID"
                        }
                    },
                    {
                        "exists": {
                            "field": "External TweetID"
                        }
                    }
                    ]
                }
            }
        }
    )
        
    hit_count = len(results["hits"]["hits"])
    print("%d hits" % hit_count)
    random_doc_index = random.randint(1,hit_count)
    print(random_doc_index)
    tweet_id = results["hits"]["hits"][random_doc_index-1]["_source"]["TweetID"]
    ext_tweet_id = results["hits"]["hits"][random_doc_index-1]["_source"]["External TweetID"]
    random_tweet_id = tweet_id if tweet_id != None else ext_tweet_id
    print(random_tweet_id)
    return(random_tweet_id)

def get_a_random_book() :
    index_name = "booklist"
    docs_count = client.count(index=index_name)['count']
    print("docs_count = %d" % docs_count)
    random_doc_id = random.randint(1,docs_count)
    print("generate random doc_id = %d" % random_doc_id)
    doc = client.get(index=index_name, id=str(random_doc_id))
    print(doc)
    #print(doc["_source"]["Book Title"])
    #print(doc["_source"]["Author"])
    #print(doc["_source"]["Year Published"])
    bookinfo = "Title: " + doc["_source"]["Book Title"] + ".  Author: " + doc["_source"]["Author"] + ".  Year Published: " + doc["_source"]["Year Published"]
    print(bookinfo)
    return(bookinfo)

def get_all_book() :
    results=client.search(index="booklist",body={"size":999,"query":{"match_all":{}}})
    hit_count = len(results["hits"]["hits"])
    print("%d hits" % hit_count)
    allbooks = results["hits"]["hits"]
    print(allbooks)
    return(allbooks, hit_count)   

def get_all_love_quotes() :    
    results=client.search(index="lovequotelist",body={"size":999,"query":{"match_all":{}}})
    hit_count = len(results["hits"]["hits"])
    print("%d hits" % hit_count)
    allrecords = results["hits"]["hits"]
    print(allrecords)
    return(allrecords, hit_count)

def get_all_words() :    
    results=client.search(index="wordlist",body={"size":999,"query":{"match_all":{}}})
    hit_count = len(results["hits"]["hits"])
    print("%d hits" % hit_count)
    allrecords = results["hits"]["hits"]
    print(allrecords)
    return(allrecords, hit_count)

def get_all_quotes() :    
    results=client.search(index="quotelist",body={"size":999,"query":{"match_all":{}}})
    hit_count = len(results["hits"]["hits"])
    print("%d hits" % hit_count)
    allrecords = results["hits"]["hits"]
    print(allrecords)
    return(allrecords, hit_count)

def get_all_subscribers():
    index_name = "subscriptionlist"
    results=client.search(index=index_name,body={"size":999,"query":{"match_all":{}}})
    hit_count = len(results["hits"]["hits"])
    print("%d hits" % hit_count)
    allrecords = results["hits"]["hits"]
    print(allrecords)
    return(allrecords, hit_count)

def get_all_subscribers_test():
    index_name = "subscriptionlist_test"
    results=client.search(index=index_name,body={"size":999,"query":{"match_all":{}}})
    hit_count = len(results["hits"]["hits"])
    print("%d hits" % hit_count)
    allrecords = results["hits"]["hits"]
    print(allrecords)
    return(allrecords, hit_count)

def add_a_subscription(email, interest) :
    client.index(index='ingestsubscriptionlist', doc_type='post', body= \
    {
        'Email': email,
        'Interest': interest
    })

def remove_a_subscription(email) :
    client.index(index='unsubscriptionlist', doc_type='post', body= \
    {
        'Email': email,
    })

def add_a_love_quote(quote, author) :
    client.index(index='lovequotelist_new', doc_type='post', body= \
    {
        'Quote': quote,
        'Author': author
    })

def add_a_comment(comment, author) :
    client.index(index='commentlist', doc_type='post', body= \
    {
        'Comment': comment,
        'Author': author
    })

def global_copy(text) :
    client.index(index='globalcopypaste', id="1", body= \
    {
        'Text': text
    })

def global_paste() :
    try:
        doc = client.get(index='globalcopypaste', id="1")
        print(doc)
        return doc["_source"]["Text"]
    except:
        return ""

def file_upload(filename) :
    client.index(index='globalfiletransfer', id="1", body= \
    {
        'File Name': filename
    })

def file_download() :
    try:
        doc = client.get(index='globalfiletransfer', id="1")
        print(doc)
        return doc["_source"]["File Name"]
    except:
        return ""

def save_blog(date, title, text) :
    index_name = "blog"
    if client.indices.exists(index_name) == False:
        print("es save_blog, index does not exist, create the first entry")
        id = 1 #first entry
    else:
        id = client.count(index=index_name)['count']
        print("save_blog, docs_count = %d" % id)
        id = id+1
    print("id= %s" % str(id))
    client.index(index='blog', id=str(id), body= \
    {
        'Date': date,
        'Title' : title,
        'Text': text
    })
    return

def get_latest_blog() :
    index_name = "blog"
    id = client.count(index=index_name)['count']
    print("docs_count = %d" % id)
    doc = client.get(index=index_name, id=str(id))
    return doc["_source"]["Date"], doc["_source"]["Title"], doc["_source"]["Text"]

def get_all_blogs() :
    index_name = "blog"
    results=client.search(index=index_name,body={"size":999,"query":{"match_all":{}}})
    hit_count = len(results["hits"]["hits"])
    allblogs = results["hits"]["hits"]
    print(allblogs)
    return(allblogs, hit_count) 
#test
#for num, doc in enumerate(results["hits"]["hits"]): 
#    print("index = %d" % num)
#    print(doc)

#get_a_random_book_tweet_id()