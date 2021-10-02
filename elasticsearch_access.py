import random
from elasticsearch import Elasticsearch
from datetime import datetime

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
    return(doc["_source"]["Quote"], doc["_source"]["Author"], doc["_source"]["TweetID"])

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
    return(doc["_source"]["Photo File Name"])

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
    bookinfo = "Title: " + doc["_source"]["Book Title"] + ".  Author: " + doc["_source"]["Author"] + ".  Year Published: " + doc["_source"]["Year Published"]
    bookimage = doc["_source"]["Image File Name"]
    print(bookinfo)
    return(bookinfo, bookimage)

def get_total_book_count() :
    index_name = "booklist"
    docs_count = client.count(index=index_name)['count']
    print("docs_count = %d" % docs_count)
    return(docs_count)

def get_all_book() :
    results=client.search(index="booklist",body={"size":999,"query":{"match_all":{}}})
    hit_count = len(results["hits"]["hits"])
    #print("%d hits" % hit_count)
    allbooks = results["hits"]["hits"]
    #print(allbooks)
    return(allbooks, hit_count)   

def get_book_statistics():
    index_name = "booklist"
    #total_count = client.count(index=index_name)['count']
    allbooks, total_count = get_all_book()

    results=client.count(index=index_name, body=\
    {
        "query": {
            "match": {
                "Genre": {
                    "query": "Fiction"
                }
            }
        }
    })
    fiction_count = results["count"]
    nonfiction_count = total_count - fiction_count

    #query "Audio Book" return invalid result as ES/query does not search exact string
    #query "Audio" return correct result
    #For same reason, query "Book" will not return physical book count
    results=client.count(index=index_name, body=\
    {
        "query": {
            "match": {
                "Book Type": {
                    "query": "Audio"
                }
            }
        }
    })
    audio_book_count = results["count"]
    results=client.count(index=index_name, body=\
    {
        "query": {
            "match": {
                "Book Type": {
                    "query": "EBook"
                }
            }
        }
    })
    ebook_count = results["count"]
    phy_book_count = total_count - audio_book_count - ebook_count

    ''' aggregration on text field not possible
    results=client.search(index=index_name, body=\
    {
        "aggs": {
            "avg_page_count": { "avg": { "field": "Page Count" } }
        }
    })
    avg_page_count = results["aggregations"]["avg_page_count"]
    '''

    min_page_count = 500
    max_page_count = 0
    total_page_count = 0
    count = 0
    books_read_2018 = 0
    books_read_2019 = 0
    books_read_2020 = 0
    books_read_2021 = 0
    books_published_2000s = 0
    books_published_1900s = 0
    books_published_1800s = 0
    oldest_book = 2021
    shortest_book_image = ""
    oldest_book_image = ""
    longest_book_image = ""
    books_rated_5 = 0
    books_rated_4 = 0
    books_rated_3 = 0
    for doc in allbooks:
        if( doc["_source"]["Page Count"] != None ) :            
            page_count = int(doc["_source"]["Page Count"])
            count += 1
            total_page_count = total_page_count + page_count
            if( page_count < min_page_count ):
                min_page_count = page_count
                shortest_book_image = doc["_source"]["Image File Name"]
            if( page_count > max_page_count ):
                max_page_count = page_count
                longest_book_image = doc["_source"]["Image File Name"]
        if( doc["_source"]["Date Finished"] != None ) :
            try: 
                year = datetime.strptime(doc["_source"]["Date Finished"], '%m/%d/%Y').year
            except: 
                try :
                    year = datetime.strptime(doc["_source"]["Date Finished"], '%Y').year
                except:
                    print("datetime parse exception %s" % doc["_source"]["Date Finished"])          
            if( year <= 2018 ) :
                books_read_2018 += 1
            elif( year == 2019 ) :
                books_read_2019 += 1
            elif( year == 2020 ) :
                books_read_2020 += 1
            else :
                books_read_2021 += 1

        if( doc["_source"]["Year Published"] != None ) :
            year = int(doc["_source"]["Year Published"])
            if( year >= 2000 ) :
                books_published_2000s += 1
            elif( year >= 1900 ) :
                books_published_1900s += 1
            else :
                books_published_1800s += 1
            if( year < oldest_book ) :
                oldest_book = year
                oldest_book_image = doc["_source"]["Image File Name"]

        if( doc["_source"]["Rating"] != None ) :
            if( len(doc["_source"]["Rating"]) == 5 ) :
                books_rated_5 += 1
            elif( len(doc["_source"]["Rating"]) == 4 ) :
                books_rated_4 += 1
            elif( len(doc["_source"]["Rating"]) == 3 ) :
                books_rated_3 += 1

    avg_page_count = int(total_page_count / count)
    print("min_page_count: %d" % min_page_count)
    print("max_page_count: %d" % max_page_count)
    print("total_page_count: %d" % total_page_count)
    print("avg_page_count: %d" % avg_page_count)
    print("books rated 5: %d" % books_rated_5)
    print("books rated 4: %d" % books_rated_4)
    print("books rated 3: %d" % books_rated_3)

    book_stats = \
    {
        "total count": total_count,
        "fiction count": fiction_count,
        "nonfiction count": nonfiction_count,
        "physical book count": phy_book_count,
        "ebook count": ebook_count,
        "audio book count": audio_book_count,
        "min page count": min_page_count,
        "max page count": max_page_count,
        "total page count": total_page_count,
        "total word count": total_page_count*299, # 250-300 words per page
        "average page count": avg_page_count,
        "books read in 2018 and prior": books_read_2018,
        "books read in 2019": books_read_2019,
        "books read in 2020": books_read_2020,
        "books read in 2021": books_read_2021,
        "books published in 2000s": books_published_2000s,
        "books published in 1900s": books_published_1900s,
        "books published in 1800s and prior": books_published_1800s,
        "oldest book in year": oldest_book,
        "oldest book image": oldest_book_image,
        "shortest book image": shortest_book_image,
        "longest book image": longest_book_image,
        "books rated 5": books_rated_5,
        "books rated 4": books_rated_4,
        "books rated 3": books_rated_3
    }
    return book_stats

def get_all_twitter_books():
    index_name = "twitterbooklist"
    results=client.search(index=index_name, body=\
    {
        "size":999,
        "query":{"match_all":{}},
        "sort" : [ { "Likes" : "desc" } ]
    })
    hit_count = len(results["hits"]["hits"])
    alldocs = results["hits"]["hits"]
    return alldocs, hit_count

def get_all_twitter_books_from_booklist():
    index_name = "booklist"
    results=client.search(index=index_name, body=\
    {
        "size":999,
        "query": {
            "exists": {
                "field": "TweetID"
            }
        }
    })
    hit_count = len(results["hits"]["hits"])
    alldocs = results["hits"]["hits"]
    return alldocs, hit_count

def add_a_twitter_book(tweet_id, likes, nonfiction) :
    index_name = "twitterbooklist"
    client.index(index=index_name, doc_type='post', body= \
    {
        'TweetID': tweet_id,
        'Likes': likes,
        'Nonfiction': nonfiction
    })

def delete_twitter_book_index():
    index_name = "twitterbooklist"
    client.indices.delete(index=index_name, ignore=[400, 404])

def create_twitter_book_index():
    index_name = "twitterbooklist"
    client.indices.create(index=index_name)

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

def save_journal(date, title, text, type) :
    index_name = "journal"
    if client.indices.exists(index_name) == False:
        print("es save_journal, index does not exist, create the first entry")
        id = 1 #first entry
    else:
        id = client.count(index=index_name)['count']
        print("save_journal, docs_count = %d" % id)
        id = id+1
    print("id= %s" % str(id))
    client.index(index='journal', id=str(id), body= \
    {
        'Date': date,
        'Title' : title,
        'Text': text,
        'Type': type
    })
    return


def edit_journal(id, title, text, type) :
    index_name = "journal"
    print("edit_journal, id=%s" % id)

    doc = client.get(index='journal', id=id)

    client.index(index='journal', id=str(id), body= \
    {
        'Date': doc["_source"]["Date"],
        'Title' : title,
        'Text': text,
        'Type': type
    })
    return

def get_all_journals() :
    index_name = "journal"
    results=client.search(index=index_name,body=\
    {   "size":999,
        "query":{"match_all":{}},
        "sort" : [ { "Date" : "desc" } ]
    })
    hit_count = len(results["hits"]["hits"])
    alljournals = results["hits"]["hits"]
    print(alljournals)
    return(alljournals, hit_count) 

def get_all_blogs():
    index_name = "journal"
    results=client.search(index=index_name, body=\
    {
        "query": {
            "match": {
            "Type": {
                "query": "Blog"
            }
            }
        },
        "sort" : [ { "Date" : "desc" } ]
    })
    hit_count = len(results["hits"]["hits"])
    allblogs = results["hits"]["hits"]
    return allblogs, hit_count
#test
#for num, doc in enumerate(results["hits"]["hits"]): 
#    print("index = %d" % num)
#    print(doc)

#get_a_random_book_tweet_id()
#get_a_random_quote_and_author()
#get_all_journals()
#get_book_statistics()
#get_all_twitter_books()