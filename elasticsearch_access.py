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
    results=client.search(index="wordlist",body={"size":999,"query":{"match_all":{}}})
    hit_count = len(results["hits"]["hits"])
    print("%d hits" % hit_count)
    random_index = random.randint(0,hit_count-1)
    print("generated random index = %d" % random_index)
    doc = results["hits"]["hits"][random_index]
    print(doc)
    #print(doc["_source"]["message"])
    #print(doc["_source"]["Word"])
    #print(doc["_source"]["Definition"])
    #print(doc["_source"]["Example Sentences"])
    #return(doc["_source"]["message"])
    return(doc["_source"]["Word"] + ": " + doc["_source"]["Definition"] + ".  " + doc["_source"]["Example Sentences"])

def get_a_random_quote() :    
    results=client.search(index="quotelist",body={"size":999,"query":{"match_all":{}}})
    hit_count = len(results["hits"]["hits"])
    print("%d hits" % hit_count)
    random_index = random.randint(0,hit_count-1)
    print("generated random index = %d" % random_index)
    doc = results["hits"]["hits"][random_index]
    print(doc)
    return(doc["_source"]["Quote"] + " - " + doc["_source"]["Author"])

def get_a_random_love_quote() :    
    results=client.search(index="lovequotelist",body={"size":999,"query":{"match_all":{}}})
    hit_count = len(results["hits"]["hits"])
    print("%d hits" % hit_count)
    random_index = random.randint(0,hit_count-1)
    print("generated random index = %d" % random_index)
    doc = results["hits"]["hits"][random_index]
    print(doc)
    return(doc["_source"]["Quote"]+ " - " + doc["_source"]["Author"])

def get_a_random_photo() :    
    results=client.search(index="photolist",body={"size":999,"query":{"match_all":{}}})
    hit_count = len(results["hits"]["hits"])
    print("%d hits" % hit_count)
    random_index = random.randint(0,hit_count-1)
    print("generated random index = %d" % random_index)
    doc = results["hits"]["hits"][random_index]
    print(doc)
    return(doc["_source"]["Photo File Name"])

def get_a_random_book() :    
    results=client.search(index="booklist",body={"size":999,"query":{"match_all":{}}})
    hit_count = len(results["hits"]["hits"])
    print("%d hits" % hit_count)
    random_index = random.randint(0,hit_count-1)
    print("generated random index = %d" % random_index)
    doc = results["hits"]["hits"][random_index]
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

    #doc = results["hits"]["hits"][random_index]
    #print(doc)
    allbooks = results["hits"]["hits"]
    print(allbooks)
    return(allbooks, hit_count)   
    #print(doc["_source"]["Book Title"])
    #print(doc["_source"]["Author"])
    #print(doc["_source"]["Year Published"])
    #bookinfo = "Title: " + doc["_source"]["Book Title"] + ".  Author: " + doc["_source"]["Author"] + ".  Year Published: " + doc["_source"]["Year Published"]
    #print(bookinfo)
    #return(bookinfo)

def get_all_love_quotes() :    
    results=client.search(index="lovequotelist",body={"size":999,"query":{"match_all":{}}})
    hit_count = len(results["hits"]["hits"])
    print("%d hits" % hit_count)

    #doc = results["hits"]["hits"][random_index]
    #print(doc)
    allrecords = results["hits"]["hits"]
    print(allrecords)
    return(allrecords, hit_count)

def get_all_words() :    
    results=client.search(index="wordlist",body={"size":999,"query":{"match_all":{}}})
    hit_count = len(results["hits"]["hits"])
    print("%d hits" % hit_count)

    #doc = results["hits"]["hits"][random_index]
    #print(doc)
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


def add_a_subscription(email) :
    client.index(index='subscriptionlist', doc_type='post', body= \
    {
        'Email': email,
    })

def add_a_love_quote(quote, author) :
    client.index(index='lovequotelist_new', doc_type='post', body= \
    {
        'Quote': quote,
        'Author': author
    })

#test
#for num, doc in enumerate(results["hits"]["hits"]): 
#    print("index = %d" % num)
#    print(doc)
