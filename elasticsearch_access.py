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
    #print(doc)
    #print(doc["_source"]["message"])
    #print(doc["_source"]["Word"])
    #print(doc["_source"]["Definition"])
    #print(doc["_source"]["Example Sentences"])
    #return(doc["_source"]["message"])
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

#test
#for num, doc in enumerate(results["hits"]["hits"]): 
#    print("index = %d" % num)
#    print(doc)
