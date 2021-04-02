import os
from flask import Flask
from flask import render_template
from flask import request, redirect
from flask import flash, url_for
from flask import jsonify
import json

import file_mgr

import elasticsearch_access
import random

import smtplib, ssl	
sender_email = "whereliteraturemeetscomputing@gmail.com"
receiver_email = "whope2@gmail.com"
port = 465  # For SSL

UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "secret key"

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        
@app.route('/')
def index():

	#get a random photo from Instagam
	photolist = [ "CM4PMeIhQ0n", "CMkTiEcAydu", "CMZbmfDBDwr", "CMXK6TQhQj2", "CMUNyMXBje4", "CLwNyIxBWB3", "CKyY8uOB5Vb", "CHc_XsahcVH", "CF55n-ZB_-w", "CM5g3mOHNCR",
	 "CF8Krp9BvpF", "CATF5idhkNQ", "B9-ZkJ3FozY", "B-ZYFl-F4lo", "B-qFAdzBpal", "B-vPV2pBLqd", "B_yJRLAhmgp", "CMwkKCphTYg", "CMzFmO_h9do", "CMgJbhzhoaQ"]
	photo_count = len(photolist)
	random_count = random.randint(0,photo_count-1)
	photolink = photolist[random_count]
	
	random_quote = elasticsearch_access.get_a_random_quote()
	random_word = elasticsearch_access.get_a_random_word()
	random_book = elasticsearch_access.get_a_random_book()
	random_love_quote = elasticsearch_access.get_a_random_love_quote()	
	return render_template('index.html',word=random_word,quote=random_quote,photolink=photolink,book=random_book,love_quote=random_love_quote)
	
@app.route('/echo_search')
def echo_search():
	return render_template('echo_search.html')

@app.route("/<name>")
def hello_name(name):
    #return "Hello " + name
	#return render_template('echo.html', text=name)
	return render_template('index.html', name=name)

import requests
@app.route("/elasticsearch/<args>")
def route_es_args(args):
	url = request.full_path
	es_url = url.replace("/elasticsearch","http://localhost:9200")
	print(es_url)
	#return(redirect(es_url))
	try: 
		es_result = requests.get(es_url).json()  #Es throws an exception if not json format
	except ValueError:
		es_result = requests.get(es_url).content
	print(es_result)
	return(es_result)

@app.route("/elasticsearch/<es_api>/<args>")
def route_es_api_args(es_api,args):
	url = request.full_path
	es_url = url.replace("/elasticsearch","http://localhost:9200")
	print(es_url)
	#return(redirect(es_url))
	try: 
		es_result = requests.get(es_url).json()  #Es throws an exception if not json format
	except ValueError:
		es_result = requests.get(es_url).content
	print(es_result)
	return(es_result)

@app.route("/stat")
def stat():
	#stat_json = elasticsearch_access.stat_wordlist()
	#return stat_json	
	instruction = "Use the browser and elasticsearch api: \n\
/elasticsearch/_cat/indices \n\
/elasticsearch/quotelist/_search?pretty=true \n\
/elasticsearch/wordlist/_search?pretty=true&size=20"
	print(instruction)
	flash(instruction)
	return redirect('/')

@app.route("/pictureoftheday")
def pictureoftheday():
	return redirect('/')

@app.route("/quoteoftheday")
def quoteoftheday():
	allrecords, count = elasticsearch_access.get_all_quotes()
	#count=10  #test
	items = [{}] * count
	oneitem = {}
	for num, doc in enumerate(allrecords):
		oneitem["Quote"] = doc["_source"]["Quote"]
		oneitem["Author"] = doc["_source"]["Author"]
		print(oneitem)
		items[num] = oneitem.copy()  #use copy() or deepcopy instead of assigning dict directly, which copes reference not value
	col_names=["Quote","Author"]
	col_width={
		'Quote':"75%",
		'Author':"25%"
	}

	random_i = random.randint(0,count-1)
	return render_template('quotelist.html', col_names=col_names, col_width=col_width, items=items, count=count, \
		quote=items[random_i]["Quote"]+ " - " + items[random_i]["Author"])

#api: /genwordoftheday/
#Generate a random word
#Redirect to /wordoftheday?word=... to render the wordsmart.html template
@app.route("/genwordoftheday")
def genwordoftheday():

	#Generate a random word
	#The following code can be simplified. No need to retreive all words from ES
	allrecords, count = elasticsearch_access.get_all_words()
	#count=10  #test
	items = [{}] * count
	oneitem = {}
	for num, doc in enumerate(allrecords):
		oneitem["Word"] = doc["_source"]["Word"]
		oneitem["Definition"] = doc["_source"]["Definition"]
		oneitem["Example Sentences"] = doc["_source"]["Example Sentences"]
		#print(oneitem)
		items[num] = oneitem.copy()  #use copy() or deepcopy instead of assigning dict directly, which copes reference not value
		#if num == count-1: #test
		#	break
	col_names=["Word","Definition","Example Sentences"]
	col_width={
		'Word':"25%",
		'Definition':"25%",
		'Example Sentences':"50%"
	}

	random_i = random.randint(0,count-1)
	word = items[random_i]["Word"]
	defi = items[random_i]["Definition"]
	sens = items[random_i]["Example Sentences"]

	url = url_for('wordoftheday') + "?word=%s&def=%s&sens=%s" % (word,defi,sens) 
	print(url)

	return redirect(url)

#api: /wordoftheday/
#one   args: Use the arg as the word
#two   args: The first is word, the second is def
#three args: The first is word, the second is def, the third sentenses.
@app.route("/wordoftheday")
def wordoftheday():
	arg_count = len(request.args)
	word = arg_word = request.args.get('word')
	defi = arg_defi = request.args.get('def')
	sens = arg_sens = request.args.get('sens')
	print(arg_word)
	print(arg_defi)
	print(arg_sens)

	allrecords, count = elasticsearch_access.get_all_words()
	#count=10  #test
	items = [{}] * count
	oneitem = {}
	for num, doc in enumerate(allrecords):
		oneitem["Word"] = doc["_source"]["Word"]
		oneitem["Definition"] = doc["_source"]["Definition"]
		oneitem["Example Sentences"] = doc["_source"]["Example Sentences"]
		urlt = url_for('wordoftheday') + "?word=%s&def=%s&sens=%s" % (doc["_source"]["Word"],doc["_source"]["Definition"],doc["_source"]["Example Sentences"]) 
		url = urlt.replace(" ", "%20")
		oneitem["URL"] = url
		print(oneitem)
		items[num] = oneitem.copy()  #use copy() or deepcopy instead of assigning dict directly, which copes reference not value
		#if num == count-1: #test
		#	break
	col_names=["Word","Definition","Example Sentences"]
	col_width={
		'Word':"25%",
		'Definition':"25%",
		'Example Sentences':"50%"
	}

	if arg_word == None :
		random_i = random.randint(0,count-1)
		word = items[random_i]["Word"]
		defi = items[random_i]["Definition"]
		sens = items[random_i]["Example Sentences"]

	return render_template("wordsmart.html", col_names=col_names, col_width=col_width, items=items, count=count, \
		word=word, defi=defi, sens=sens)

@app.route("/liveathousandlives")
def liveathousandlives():

	#get a list of my book posts from Twitter
	booklist = [ 
		"1369445515784491020", #Great Alone
		"1374465337375158278", #Silent patient
		"1377976696742281216", #born a crime
		"1377381280254472195", #Hobbit
		"1371854745426653187", #Know my name
		"1370492268034060293", #a promised land
		"1367157299882708994", #hillbilly elegy
		"1363941579405279240", #give of stars
		"1360372421921038336", #vanishing half
		]
	bookcount = len(booklist)

	allbooks, count = elasticsearch_access.get_all_book()
	items = [{}] * count
	oneitem = {}
	for num, doc in enumerate(allbooks):
		oneitem["Book Title"] = doc["_source"]["Book Title"]
		oneitem["Author"] = doc["_source"]["Author"]
		oneitem["Year Published"] = doc["_source"]["Year Published"]
		oneitem["Date Finished"] = doc["_source"]["Date Finished"]
		#print(oneitem)
		items[num] = oneitem.copy()  #use copy() or deepcopy instead of assigning dict directly, which copes reference not value
	columns=["Book Title","Author","Year Published","Date Finished"]
	random_i = random.randint(0,count-1)
	return render_template('booklist.html', columns=columns, items=items, count=count,\
		booklist=booklist, bookcount=bookcount)

@app.route("/about")
def about():
	line1 = "Welcome to my personal website ─"
	line2 = "Where Literature Meets Computing!"
	line3 = "Enjoy daily photo, daily quote, daily smart word, daily love quote, and daily book!"
	line4 = "Subscribe to receive it in your inbox!"
	return render_template('about.html', line1=line1, line2=line2, line3=line3, line4=line4)

@app.route("/whatloveis")
def whatloveis():
	allrecords, count = elasticsearch_access.get_all_love_quotes()
	items = [{}] * count
	oneitem = {}
	for num, doc in enumerate(allrecords):
		oneitem["Quote"] = doc["_source"]["Quote"]
		#oneitem["Author"] = doc["_source"]["Author"]
		#print(oneitem)
		items[num] = oneitem.copy()  #use copy() or deepcopy instead of assigning dict directly, which copes reference not value
	columns=["Quote"] #,"Author"]
	return render_template('lovequotelist.html', columns=columns, items=items, count=count, love_quote=oneitem["Quote"])

@app.route("/subscribe", methods=['POST'])
def subscribe():
	email = request.form['email']
	elasticsearch_access.add_a_subscription(email)

	#email notification
	message = """\
	Subject: WLMC - New subscription!

	This message is sent from Python."""
	#password = input("Type your password and press enter: ")
	password = file_mgr.get_pw()
	# Create a secure SSL context
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
		server.login(sender_email, password)
		server.sendmail(sender_email, receiver_email, message)

	return render_template('echo.html', text="Thanks for your subscription!")

@app.route("/addlovequote", methods=['POST'])
def addlovequote():
	quote = request.form['QuoteText']
	author = request.form['QuoteAuthor']
	elasticsearch_access.add_a_love_quote(quote, author)
	
	#email notification
	message = """\
	Subject: WLMC - love quote entered

	This message is sent from Python."""
	#password = input("Type your password and press enter: ")
	password = file_mgr.get_pw()
	# Create a secure SSL context
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
		server.login(sender_email, password)
		server.sendmail(sender_email, receiver_email, message)

	return render_template('echo.html', text="Thanks for your contribution!")

@app.route("/postcomment", methods=['POST'])
def postcomment():
	comment = request.form['CommentText']
	author = request.form['CommentAuthor']
	elasticsearch_access.add_a_comment(comment, author)
	
	#email notification
	message = """\
	Subject: WLMC - a comment added

	This message is sent from Python."""
	#password = input("Type your password and press enter: ")
	password = file_mgr.get_pw()
	# Create a secure SSL context
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
		server.login(sender_email, password)
		server.sendmail(sender_email, receiver_email, message)

	return render_template('echo.html', text="Thanks for your comment!")

@app.after_request
def add_header(response):
	response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
	response.headers["Pragma"] = "no-cache" # HTTP 1.0.
	response.headers["Expires"] = "0" # Proxies.	
	return response


if __name__ == '__main__':
	#app.run(port=5002,debug=False)
	app.run(host='0.0.0.0',port=80)
