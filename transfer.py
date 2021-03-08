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
	file_name = elasticsearch_access.get_a_random_photo()
	file_path = "static/uploads/"+file_name
	random_quote = elasticsearch_access.get_a_random_quote()
	random_word = elasticsearch_access.get_a_random_word()
	random_book = elasticsearch_access.get_a_random_book()
	random_love_quote = elasticsearch_access.get_a_random_love_quote()	
	return render_template('index.html',word=random_word,quote=random_quote,photo=file_path,book=random_book,love_quote=random_love_quote)
	
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
	photo_path = elasticsearch_access.get_a_random_photo()
	#print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='uploads/' + photo_path), code=301)

@app.route("/quoteoftheday")
def quoteoftheday():
	#random_quote = elasticsearch_access.get_a_random_quote()
	#print(random_quote)
	#return render_template('echo.html', text="Quote of The Day: " + random_quote)

	allrecords, count = elasticsearch_access.get_all_quotes()
	#count=10  #test
	items = [{}] * count
	oneitem = {}
	for num, doc in enumerate(allrecords):
		oneitem["Quote"] = doc["_source"]["Quote"]
		oneitem["Author"] = doc["_source"]["Author"]
		print(oneitem)
		items[num] = oneitem.copy()  #use copy() or deepcopy instead of assigning dict directly, which copes reference not value
		#if num == count-1: #test
		#	break
	col_names=["Quote","Author"]
	col_width={
		'Quote':"75%",
		'Author':"25%"
	}

	random_i = random.randint(0,count-1)
	return render_template('quotelist.html', col_names=col_names, col_width=col_width, items=items, count=count, \
		quote=items[random_i]["Quote"]+ " - " + items[random_i]["Author"])


@app.route("/wordoftheday")
def wordoftheday():
	allrecords, count = elasticsearch_access.get_all_words()
	#count=10  #test
	items = [{}] * count
	oneitem = {}
	for num, doc in enumerate(allrecords):
		oneitem["Word"] = doc["_source"]["Word"]
		oneitem["Definition"] = doc["_source"]["Definition"]
		oneitem["Example Sentences"] = doc["_source"]["Example Sentences"]
		print(oneitem)
		items[num] = oneitem.copy()  #use copy() or deepcopy instead of assigning dict directly, which copes reference not value
		#if num == count-1: #test
		#	break
	#columns=["Word","Definition","Example Sentences"]
	col_names=["Word","Definition","Example Sentences"]
	col_width={
		'Word':"25%",
		'Definition':"25%",
		'Example Sentences':"50%"
	}

	random_i = random.randint(0,count-1)
	return render_template('wordsmart.html', col_names=col_names, col_width=col_width, items=items, count=count, \
		word=items[random_i]["Word"], wordoftheday=items[random_i]["Word"]+ ": " + items[random_i]["Definition"]+ ". " + items[random_i]["Example Sentences"])

@app.route("/liveathousandlives")
def liveathousandlives():
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
		book="Book Title: "+items[random_i]["Book Title"]+ ".  Author: " + items[random_i]["Author"]+ ".  Year Published: " + items[random_i]["Year Published"])

@app.route("/about")
def about():
	about_text = "Welcome to my personal website, where literature meets computing!\r\n\
	Enjoy daily photo, daily quote, daily word, daily book, and many more!\r\n\
	Subscribe to receive it in your inbox!"
	return render_template('echo.html', text=about_text)

@app.route("/whatloveis")
def whatloveis():
	allrecords, count = elasticsearch_access.get_all_love_quotes()
	items = [{}] * count
	oneitem = {}
	for num, doc in enumerate(allrecords):
		oneitem["Quote"] = doc["_source"]["Quote"]
		oneitem["Author"] = doc["_source"]["Author"]
		#print(oneitem)
		items[num] = oneitem.copy()  #use copy() or deepcopy instead of assigning dict directly, which copes reference not value
	columns=["Quote","Author"]
	return render_template('lovequotelist.html', columns=columns, items=items, count=count, love_quote=oneitem["Quote"]+" - "+oneitem["Author"])

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

@app.after_request
def add_header(response):
	response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
	response.headers["Pragma"] = "no-cache" # HTTP 1.0.
	response.headers["Expires"] = "0" # Proxies.	
	return response


if __name__ == '__main__':
	#app.run(port=5000,debug=False)
	app.run(host='0.0.0.0',port=80)
