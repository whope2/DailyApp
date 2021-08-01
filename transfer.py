import os
from flask import Flask
from flask import render_template
from flask import request, redirect
from flask import url_for
from flask import jsonify
import json

import file_mgr

import elasticsearch_access
import random
import requests

#from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

import smtplib, ssl	
from email.message import EmailMessage
sender_email = "whereliteraturemeetscomputing@gmail.com"
myemail = "whope2@gmail.com"
port = 465  # For SSL

import twitterbot

UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "secret key"

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        
@app.route('/')
def index():
	arg_count = len(request.args)
	email = "..."
	if( arg_count > 0):
		email = request.args.get('email')
		print("index %s" % email)

	photo_id, media_id, image_url = elasticsearch_access.get_a_random_photo()
	random_quote = elasticsearch_access.get_a_random_quote()

	doc_word = elasticsearch_access.get_a_random_word()
	random_word = doc_word["Word"] + ": " + doc_word["Definition"] + ".  " + doc_word["Example Sentences"]

	random_book = elasticsearch_access.get_a_random_book()
	random_love_quote = elasticsearch_access.get_a_random_love_quote()	
	return render_template('index.html',word=random_word,quote=random_quote,photolink=photo_id,book=random_book,love_quote=random_love_quote,email=email)
	
@app.route('/echo_search')
def echo_search():
	return render_template('echo_search.html')

@app.route("/<name>")
def hello_name(name):
    #return "Hello " + name
	#return render_template('echo.html', text=name)
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

	#Get a random word from ES
	doc = elasticsearch_access.get_a_random_word()
	word = doc["Word"]
	defi = doc["Definition"]
	sens = doc["Example Sentences"]
	#prepare url with arguments for a new endpoint
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

	if defi == None :
		dict_api_url = \
		"https://dictionaryapi.com/api/v3/references/collegiate/json/\
		%s?key=77e0d2f9-1fcf-482e-a786-be6cc82ec61e" % (word)	
		dict_api_result = requests.get(dict_api_url).json()
		print(dict_api_result)
		try :
			def_list = dict_api_result[0]["shortdef"]
			#defi = def_list[0] #the first definition
			#get all definitions
			defi = ""
			for one_def in def_list:
				defi += one_def
				defi += "; "
			print(defi)
			
			sens= dict_api_result[0]["def"][0]["sseq"][0][0][1]["dt"][1][1][0]["t"]
			print(sens)
		except :
			print("dict api return error - word not found")

	#get all words to populate the table
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

@app.route("/searchaword", methods=['POST'])
def searchaword():
	word = request.form['searchaword']
	url = url_for('wordoftheday') + "?word=%s" % (word) 
	print(url)
	return redirect(url)

@app.route("/liveathousandlives")
def liveathousandlives():
	#get a list of my book posts from Twitter
	booklist = []
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
		if doc["_source"]["TweetID"] != None :  #if not an empty
			booklist.append( doc["_source"]["TweetID"] ) #add to the list
	
	random.shuffle(booklist)
	bookcount = len(booklist)
	columns=["Book Title","Author","Year Published","Date Finished"]
	random_i = random.randint(0,count-1)
	return render_template('booklist.html', columns=columns, items=items, count=count,\
		booklist=booklist, bookcount=bookcount)

@app.route("/about")
def about():
	return render_template('about.html')

@app.route("/whatloveis")
def whatloveis():
	allrecords, count = elasticsearch_access.get_all_love_quotes()
	items = [{}] * count
	oneitem = {}
	random_i = random.randint(0,count-1)
	for num, doc in enumerate(allrecords):
		oneitem["Quote"] = doc["_source"]["Quote"]
		#oneitem["Author"] = doc["_source"]["Author"]
		#print(oneitem)
		items[num] = oneitem.copy()  #use copy() or deepcopy instead of assigning dict directly, which copes reference not value
	columns=["Quote"] #,"Author"]
	return render_template('lovequotelist.html', columns=columns, items=items, count=count, love_quote=items[random_i]["Quote"])

def email_notify_me(subject, content):
	#email notification
	message = EmailMessage()
	message.set_content(content)
	message['Subject'] = subject
	message['From'] = sender_email
	message['To'] = myemail
	#password = input("Type your password and press enter: ")
	password = file_mgr.get_pw()
	# Create a secure SSL context
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
		server.login(sender_email, password)
		server.send_message(message)

#/prescribe?email=...
@app.route("/presubscribe")
def presubscribe():
	arg_count = len(request.args)
	email = request.args.get('email')
	print("presubscribe %s" % email)
	#prepare url with arguments for a new endpoint
	url = url_for('index') + "?email=%s#sub" % (email) 
	print(url)
	return redirect(url)

@app.route("/subscribe", methods=['POST'])
def subscribe():
	email = request.form['email']
	#prepare the interest string from the form request (e.g. "Quote,Book,Word")
	interest = ""
	if( "interest_photo" in request.form ):
		interest += ",Photo"
	if( "interest_quote" in request.form ):
		interest += ",Quote"
	if( "interest_book" in request.form ):
		interest += ",Book"
	if( "interest_word" in request.form ):
		interest += ",Word"
	if( "interest_lovequote" in request.form ):
		interest += ",Love"
	#strip the first comma if it exists
	if( interest[0] == ",") :
		interest = interest[1:]

	elasticsearch_access.add_a_subscription(email, interest)
	email_notify_me("TWLMC - New subscription!", ("from: %s" % email))

	return render_template('echo.html', text="Thanks for your subscription!")

@app.route("/unsubscribe")
def unsubscribe():
	arg_count = len(request.args)
	email = request.args.get('email')
	print("unsubscribe %s" % email)
	elasticsearch_access.remove_a_subscription(email)
	email_notify_me("TWLMC - Unsubscription", ("from: %s" % email))
	return render_template('echo.html', text="Sorry to see you leave. Have a great day!")

@app.route("/addlovequote", methods=['POST'])
def addlovequote():
	quote = request.form['QuoteText']
	author = request.form['QuoteAuthor']
	elasticsearch_access.add_a_love_quote(quote, author)
	email_notify_me("TWLMC - a love quote added!", "quote: %s, author: %s" % (quote, author))
	return render_template('echo.html', text="Thanks for your contribution!")

@app.route("/postcomment", methods=['POST'])
def postcomment():
	comment = request.form['CommentText']
	author = request.form['CommentAuthor']
	elasticsearch_access.add_a_comment(comment, author)
	email_notify_me("WLMC - a comment added!", "comment: %s, author: %s" % (comment, author))
	return render_template('echo.html', text="Thanks for your comment!")

@app.after_request
def add_header(response):
	response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
	response.headers["Pragma"] = "no-cache" # HTTP 1.0.
	response.headers["Expires"] = "0" # Proxies.	
	return response

def ig_shortcode_to_media_id(short_code):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
    media_id = 0
    for letter in short_code:
        media_id = (media_id*64) + alphabet.index(letter)

    return media_id

TESTING_NEWSLETTER = False
def newsletter():
	global TESTING_NEWSLETTER
	print("Produce Newsletter! The time is: %s" % datetime.now())
	
	#prepare newsletter content
	random_quote = elasticsearch_access.get_a_random_quote()
	doc_word = elasticsearch_access.get_a_random_word()
	random_word = doc_word["Word"] + ": " + doc_word["Definition"] + ".  " + doc_word["Example Sentences"]
	random_book = elasticsearch_access.get_a_random_book()
	random_love_quote = elasticsearch_access.get_a_random_love_quote()
	photo_id, media_id, image_url = elasticsearch_access.get_a_random_photo()

	#media_id_gen = ig_shortcode_to_media_id(photo_id)
	
	newsletter_prefix = "Welcome to our nascent Literature Newsletter!\n\n"

	#prepare email
	message = EmailMessage()
	message['Subject'] = "Literature Newsletter"
	message['From'] = sender_email
	
	password = file_mgr.get_pw()
	# Create a secure SSL context
	context = ssl.create_default_context()
	server = smtplib.SMTP_SSL("smtp.gmail.com", port, context=context)
	server.login(sender_email, password)

	#get all subscriber emails from elasticsearch
	all_subscribers, count = elasticsearch_access.get_all_subscribers()
	
	for num, doc in enumerate(all_subscribers):

		newsletter_content = newsletter_prefix

		email = doc["_source"]["Email"]
		interest = doc["_source"]["Interest"]

		if( "Quote" in interest ):
			newsletter_content += "Daily Quote:\n    %s\n\n" % (random_quote)
		if( "Book" in interest ):
			newsletter_content += "Daily Book:\n    %s\n\n" % (random_book)
		if( "Word" in interest ):
			newsletter_content += "Daily Word:\n    %s\n\n" % (random_word)
		if( "Love" in interest ):
			newsletter_content += "Daily Love Quote:\n    %s\n\n" % (random_love_quote)
		if( "Photo" in interest ):
			newsletter_content += "Daily Photo:\n"
			
		#for testing, only send to my personal email
		if TESTING_NEWSLETTER == True:
			email = myemail

		message['To'] = email
		#WARNING!!! DO NOT SENT DEBUGGING MSG TO CUSTOMERS!!!
		#set content and attachment
		message.clear_content()
		message.set_content(newsletter_content)	

		if( "Photo" in interest ):
			image_url = "https://whereliteraturemeetscomputing.com/static/instagram/%s.jpg" % photo_id
			html_content_photo = '<img src="%s" alt="Photo of the Day" style="width:50%%;height:auto;"><br>' % image_url
			message.add_attachment(html_content_photo, subtype="html")

		html_content = "<br>Thanks for your time and have a nice day!<br>https://whereliteraturemeetscomputing.com"
		html_content += '\
<br><a href="https://whereliteraturemeetscomputing.com/presubscribe?email=%s#sub">Modify Subscription</a>  |  \
<a href="https://whereliteraturemeetscomputing.com/unsubscribe?email=%s">Unsubscribe</a></br>' % (email, email)	
		message.add_attachment(html_content, subtype="html")

		server.send_message(message)
		del message['To']
		
	server.quit()
	email_notify_me("WLMC - newsletter sent!", "")

#Testing trigger newsletter
@app.route("/testtriggernewsletter")
def testtriggernewsletter():
	global TESTING_NEWSLETTER
	TESTING_NEWSLETTER = True
	newsletter()
	return render_template('echo.html', text="Test Newsletter sent!")

#manually trigger newsletter first
#switch to a scheduler later
@app.route("/triggernewsletter")
def triggernewsletter():
	global TESTING_NEWSLETTER
	TESTING_NEWSLETTER = False
	newsletter()
	return render_template('echo.html', text="Newsletter sent!")

@app.route("/tweetquote")
def tweetquote():
	quote, author, tweet_id = elasticsearch_access.get_a_random_quote_and_author()
	quote2, author2, tweet_id2 = elasticsearch_access.get_a_random_quote_and_author()
	if tweet_id :
		twitterbot.tweet_quote(quote, author, tweet_id)
	else:
		twitterbot.tweet_quote(quote2, author2, tweet_id2)	
	return render_template('echo.html', text="A quote tweeted!")

@app.route("/retweetbook")
def retweetbook():
	tweet_id = elasticsearch_access.get_a_random_book_tweet_id()
	twitterbot.retweet_book(tweet_id)
	return render_template('echo.html', text="A book retweeted!")

@app.route("/copy", methods=['POST'])
def copy():
	copy_paste_text = request.form['CopyText']
	elasticsearch_access.global_copy(copy_paste_text)
	return redirect('/copypaste')

@app.route("/copypaste")
def copypaste():
	copy_paste_text = elasticsearch_access.global_paste()
	return render_template('copypaste.html', text=copy_paste_text)

@app.route("/transferfile")
def transferfile():
	filename = elasticsearch_access.file_download()
	return render_template('transferfile.html', state="download", filename=filename)

@app.route('/uploadfile', methods=['POST'])
def uploadfile():
	if 'file' not in request.files:
		#No file part
		return render_template('transferfile.html', state="No file part")
	file = request.files['file']
	if file.filename == '':
		#No file selected
		return render_template('transferfile.html', state="No file selected")

	file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
	elasticsearch_access.file_upload(file.filename)
	return render_template('transferfile.html', state=file.filename+" uploaded")

@app.route("/journal")
def journal():
	try:
		alljournals, count = elasticsearch_access.get_all_journals()
	except:
		return render_template('blog.html')	
	items = [{}] * count
	oneitem = {}
	for num, doc in enumerate(alljournals):
		oneitem = doc["_source"]
		oneitem["ID"] = doc["_id"]
		print(oneitem)
		items[num] = oneitem.copy()  #use copy() or deepcopy instead of assigning dict directly, which copes reference not value
	return render_template('blog.html', blogs=items, count=count, journaling=1)

@app.route("/blog")
def blog():
	try:
		allblogs, count = elasticsearch_access.get_all_blogs()
	except:
		return render_template('blog.html')	
	items = [{}] * count
	oneitem = {}
	for num, doc in enumerate(allblogs):
		oneitem = doc["_source"]
		print(oneitem)
		items[num] = oneitem.copy()  #use copy() or deepcopy instead of assigning dict directly, which copes reference not value
	return render_template('blog.html', blogs=items, count=count)

@app.route("/savejournal", methods=['POST'])
def savejournal():
	text = request.form['BlogText']
	title = request.form['BlogTitle']
	date = datetime.now().date()
	if( "is_blog" in request.form ):
		elasticsearch_access.save_journal(date, title, text, "blog")
	else:
		elasticsearch_access.save_journal(date, title, text, "journal")
	return redirect('/journal')

@app.route("/editjournal", methods=['POST'])
def editjournal():
	text = request.form['BlogText']
	title = request.form['BlogTitle']
	id = request.args.get("id")
	if( "is_blog" in request.form ):
		elasticsearch_access.edit_journal(id, title, text, "blog")
	else:
		elasticsearch_access.edit_journal(id, title, text, "journal")
	return redirect('/journal')

#if __name__ == '__main__':
	#app.run(port=5000,debug=False)
	#app.run(host='0.0.0.0',port=80)