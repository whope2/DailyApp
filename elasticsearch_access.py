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
    return(doc["_source"]["Author"] + ": " + doc["_source"]["Quote"])

def get_a_random_photo() :    
    results=client.search(index="photolist",body={"size":999,"query":{"match_all":{}}})
    hit_count = len(results["hits"]["hits"])
    print("%d hits" % hit_count)
    random_index = random.randint(0,hit_count-1)
    print("generated random index = %d" % random_index)
    doc = results["hits"]["hits"][random_index]
    print(doc)
    return(doc["_source"]["Photo File Name"])

#test
#for num, doc in enumerate(results["hits"]["hits"]): 
#    print("index = %d" % num)
#    print(doc)
