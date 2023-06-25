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

from operator import itemgetter #for sorting

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

	photo_id, insta_id = elasticsearch_access.get_a_random_photo()
	random_quote = elasticsearch_access.get_a_random_quote()

	doc_word = elasticsearch_access.get_a_random_word()
	random_word = doc_word["Word"] + ": " + doc_word["Definition"] + ".  " + doc_word["Example Sentences"]

	random_book, book_image = elasticsearch_access.get_a_random_book()

	sub_count = elasticsearch_access.get_subscriber_count()
	return render_template('index.html',word=random_word,quote=random_quote,photolink=photo_id,photomedia=insta_id,book=random_book,book_image=book_image,email=email,sub_count=sub_count)

@app.route('/privacy')
def privacy():
	return render_template('privacy.html')

@app.route('/apps')
def apps():
	return render_template('app.html')

@app.route('/echo_search')
def echo_search():
	return render_template('echo_search.html')

@app.route("/<name>")
def hello_name(name):
	text = '"Every one of us is losing something precious to us. Lost opportunities, lost possibilities, feelings we can never get back again. That’s part of what it means to be alive."—Haruki Murakami, Kafka on the Shore'
	return render_template('echo.html', text=text)
	#return redirect('/')

@app.route("/pictureoftheday")
def pictureoftheday():
	return redirect('/')

@app.route("/getapicallcount/<api>")
def getapicallcount(api):
	count = elasticsearch_access.apittracking_get_callcount(api)
	api_callcount_dict = {
        "api": api,
        "callcount": count
	}
	return json.dumps(api_callcount_dict)

#api - v1 - getquote, get quote & author
#api - v2 - getquote?cat="...", get a quote by category, e.g. Action, Love
@app.route("/api/getquote")
def getquote():

	arg_count = len(request.args)
	arg_cat = request.args.get('cat')
	print("api/getquote", arg_count, arg_cat)

	elasticsearch_access.apittracking_increment_callcount("getquote")

	if(arg_cat != None) :
		quote, author = elasticsearch_access.get_a_random_quote_by_category(arg_cat)
	else:
		quote, author, tweetid = elasticsearch_access.get_a_random_quote_and_author()
	
	quote_dict = {
        "quote": quote,
        "author": author
	}
	#Dictionary to JSON Object
	return json.dumps(quote_dict)

#test
#quote_ret = getquote()

#api - v1 - book & author
@app.route("/api/getbook")
def getbook():
	elasticsearch_access.apittracking_increment_callcount("getbook")
	book_title, book_author, book_year, book_image, tweet_id = elasticsearch_access.get_a_random_book_with_detail()
	dict = {
        "title": book_title,
        "author": book_author,
		"year": book_year,
		"image": book_image
	}
	#Dictionary to JSON Object
	return json.dumps(dict)

#test
#quote_ret = getbook()

#api - v1 - photo
@app.route("/api/getphoto")
def getphoto():
	elasticsearch_access.apittracking_increment_callcount("getphoto")
	image_name, media = elasticsearch_access.get_a_random_photo()
	dict = {
        "image": image_name + ".jpg"
	}
	#Dictionary to JSON Object
	return json.dumps(dict)

#test
#quote_ret = getbook()


@app.route("/quoteoftheday")
def quoteoftheday():
	arg_count = len(request.args)
	cat = request.args.get('cat')

	allrecords, count, categories = elasticsearch_access.get_all_quotes()

	if cat == None or cat not in categories :
		cat = "Love"

	cat_quote, cat_author = elasticsearch_access.get_a_random_quote_by_category(cat)

	#count=10  #test
	items = [{}] * count
	oneitem = {}
	for num, doc in enumerate(allrecords):
		oneitem["Quote"] = doc["_source"]["Quote"]
		oneitem["Author"] = doc["_source"]["Author"]
		oneitem["Category"] = doc["_source"]["Category"]
		#print(oneitem)
		items[num] = oneitem.copy()  #use copy() or deepcopy instead of assigning dict directly, which copes reference not value
	col_names=["Quote","Author"]
	col_width={
		'Quote':"75%",
		'Author':"25%"
	}

	#random.shuffle(items)
	#random_i = random.randint(0,count-1)
	return render_template('quotelist.html', col_names=col_names, col_width=col_width, items=items, count=count, \
		categories=categories, cat=cat, quote=cat_quote+ " —" + cat_author)

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

	random.shuffle(items)
	return render_template("wordsmart.html", col_names=col_names, col_width=col_width, items=items, count=count, \
		word=word, defi=defi, sens=sens)

@app.route("/searchaword", methods=['POST'])
def searchaword():
	word = request.form['searchaword']
	url = url_for('wordoftheday') + "?word=%s" % (word) 
	print(url)
	return redirect(url)

@app.route("/reviewbook")
@app.route("/liveathousandlives")
def liveathousandlives():

	bookreview = False	
	arg_count = len(request.args)
	if arg_count > 0 :
		bookid = request.args.get('bookid')
		if bookid != None :
			bookreview = True

	twitter_booklist = []
	twitter_booklist_nonfiction = []

	allbooks, count = elasticsearch_access.get_all_book_sorted_by_likes() #elasticsearch_access.get_all_book()
	items = [{}] * count
	items_sorted = [{}] * count
	oneitem = {}
	#print(count)
	for num, doc in enumerate(allbooks):
		#print(num)
		#print(doc["_source"]["id"])
		oneitem["Cover Image"] = doc["Image File Name"]
		oneitem["Book Title"] = doc["Book Title"]
		oneitem["Author"] = doc["Author"]
		oneitem["Year Published"] = doc["Year Published"]
		oneitem["My Rating"] = doc["Rating"]
		oneitem["Review"] = doc["Review"]
		oneitem["ID"] = doc["id"]
		oneitem["TweetID"] = doc["TweetID"]
		oneitem["Likes"] = doc["Likes"]
		#print(oneitem)
		items[num] = oneitem.copy()  #use copy() or deepcopy instead of assigning dict directly, which copes reference not value
		items_sorted[num] = oneitem.copy()  #use copy() or deepcopy instead of assigning dict directly, which copes reference not value

		if (doc["TweetID"] != None ):
			twitter_booklist.append(oneitem["ID"])
			if ( doc["Genre"] != "Fiction" ):
				twitter_booklist_nonfiction.append(oneitem["ID"])

	#Prepare the sorted list in python instead javascript because js does not easier provide an easy for deep copy of the original list 
	items_sorted.sort(key=itemgetter('Book Title')) 

	columns=["Cover Image","Book Title","Author","Year Published","My Rating"]

	book_stats = elasticsearch_access.get_book_statistics()

	if bookreview == False:
		bookid = random.choice(twitter_booklist)

	return render_template('booklist.html', columns=columns, items=items, items_sorted=items_sorted, count=count,\
		booklist=twitter_booklist, bookcount=len(twitter_booklist), bookreview=bookreview, bookid=bookid,\
		booklist_nonfiction=twitter_booklist_nonfiction,bookcount_nonfiction=len(twitter_booklist_nonfiction),\
		bookstats=book_stats)

@app.route("/bettereads")
def bettereads():

	allbookchats, count = elasticsearch_access.get_all_bookchat()
	items = [{}] * count
	oneitem = {}
	for num, doc in enumerate(allbookchats):
		oneitem["Text"] = doc["_source"]["Text"]
		oneitem["Date"] = doc["_source"]["Date"]
		oneitem["ID"] = doc["_source"]["id"]
		oneitem["ID-Int"] = int(doc["_source"]["id"])
		oneitem["TweetID"] = doc["_source"]["TweetID"]
		oneitem["Type"] = doc["_source"]["Type"]
		#print(oneitem)
		items[num] = oneitem.copy()  #use copy() or deepcopy instead of assigning dict directly, which copes reference not value

	items.sort(key=itemgetter('ID-Int'), reverse=True) 

	return render_template('bookchat.html', items=items, count=count)

@app.route("/about")
def about():
	book_count = elasticsearch_access.get_total_book_count()
	return render_template('about.html', book_count=book_count)

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
	interest = request.form['Interest']
	elasticsearch_access.add_a_subscription(email, interest)
	email_notify_me("TWLMC - New subscription!", ("from: %s, interest: %s" % (email,interest)))
	return render_template('echo.html', text="Thanks for your subscription!")

@app.route("/unsubscribe")
def unsubscribe():
	arg_count = len(request.args)
	email = request.args.get('email')
	interest = request.args.get('interest')
	if(interest == None):
		interest=""
	return render_template('unsubscribe.html', email=email, interest=interest)

@app.route("/unsubscribing", methods=['POST'])
def unsubscribing():
	email = request.form['email']
	try: 
		interest = request.form['interest']
	except:
		interest = ""
	print("unsubscribe %s, interest: %s" % (email,interest))
	elasticsearch_access.remove_a_subscription(email, interest)
	email_notify_me("TWLMC - Unsubscription", ("from: %s, interest: %s" % (email,interest)))
	return render_template('echo.html', text="Sorry to see you leave. Have a great day!")

@app.route("/postcomment", methods=['POST'])
def postcomment():
	comment = request.form['CommentText']
	author = request.form['CommentAuthor']
	email = request.form['CommentEmail']
	comment = comment + ", email: " + email
	elasticsearch_access.add_a_comment(comment, author)
	email_notify_me("WLMC - a comment added!", "comment: %s, author: %s" % (comment, author))
	return render_template('echo.html', text="Thanks for your comment!")

@app.after_request
def add_header(response):
	response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
	response.headers["Pragma"] = "no-cache" # HTTP 1.0.
	response.headers["Expires"] = "0" # Proxies.
	response.headers["Access-Control-Allow-Origin"] = "*"	
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
	quote, author, tweet_id = elasticsearch_access.get_a_random_quote_and_author()

	doc_word = elasticsearch_access.get_a_random_word()
	random_word = doc_word["Word"] + ": " + doc_word["Definition"] + ".  " + doc_word["Example Sentences"]
	book_title, book_author, book_year, book_image, tweet_id = elasticsearch_access.get_a_random_book_with_detail()
	photo_id, insta_id = elasticsearch_access.get_a_random_photo()

	newsletter_prefix = "Welcome to our nascent Literature Newsletter!\n"

	#prepare email
	message = EmailMessage()
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
		#testing
		#interest = "QuoteOnly"
		#interest = "BookOnly"
		#interest = "AllInOne"

		#for testing, only send to my personal email
		if TESTING_NEWSLETTER == True:
			email = myemail

		del message['To']
		del message['Subject']

		message['To'] = email
		#WARNING!!! DO NOT SENT DEBUGGING MSG TO CUSTOMERS!!!
		if( interest == "BookOnly" ):
			message['Subject'] = "Daily Book Recommendation"
		elif( interest == "QuoteOnly" ):
			message['Subject'] = "Daily Inspirational Quote"
		else:
			message['Subject'] = "Daily Literature Newsletter"
	
		#set content and attachment
		message.clear_content()
		#message.set_content(newsletter_content)	

		if(interest == "BookOnly" ):
			html_content_book = '<br><span style="font-size:4vw">Title: %s<br>Author: %s<br>Year Published: %s<br></span>&nbsp;&nbsp;&nbsp;&nbsp;' % (book_title, book_author, book_year)
			if( book_image ):
				book_url = "https://whereliteraturemeetscomputing.com/static/books/%s" % book_image
				html_content_book += '<img src="%s" alt="Book of the Day" style="width:25%%;height:auto;"><br>' % book_url
			message.add_attachment(html_content_book, subtype="html")
		elif(interest == "QuoteOnly" ):
			html_content_quote = '<br><b style="font-size:5vw">%s<br>—%s</b><br>' % (quote, author)
			message.add_attachment(html_content_quote, subtype="html")
		else:

			html_content_quote = "<br>Daily Quote:<br>&nbsp;&nbsp;&nbsp;&nbsp;%s<br>&nbsp;&nbsp;&nbsp;&nbsp;—%s</b><br>" % (quote, author)
			message.add_attachment(html_content_quote, subtype="html")
			html_content_book = "<br>Daily Book:<br>&nbsp;&nbsp;&nbsp;&nbsp;Title: %s<br>&nbsp;&nbsp;&nbsp;&nbsp;Author: %s<br>&nbsp;&nbsp;&nbsp;&nbsp;Year Published: %s<br>&nbsp;&nbsp;&nbsp;&nbsp;" % (book_title, book_author, book_year)
			if( book_image ):
				book_url = "https://whereliteraturemeetscomputing.com/static/books/%s" % book_image
				html_content_book += '<img src="%s" alt="Book of the Day" style="width:25%%;height:auto;"><br>' % book_url
			message.add_attachment(html_content_book, subtype="html")

			html_content_word = "<br>Daily Word:<br>&nbsp;&nbsp;&nbsp;&nbsp;%s<br>" % (random_word)
			message.add_attachment(html_content_word, subtype="html")

			html_content_photo = "<br>Daily Photo:<br>&nbsp;&nbsp;&nbsp;&nbsp;"
			image_url = "https://whereliteraturemeetscomputing.com/static/instagram/%s.jpg" % photo_id
			html_content_photo += '<img src="%s" alt="Photo of the Day" style="width:50%%;height:auto;"><br>' % image_url
			message.add_attachment(html_content_photo, subtype="html")

		#html_content = "<br><br><br><br><br>Thanks for your time and have a nice day!<br>https://whereliteraturemeetscomputing.com"
		html_content = "<br><br><br><br><br><br>https://whereliteraturemeetscomputing.com"
		html_content += '\
<br><a href="https://whereliteraturemeetscomputing.com/presubscribe?email=%s#sub">Modify Subscription</a>  |  \
<a href="https://whereliteraturemeetscomputing.com/unsubscribe?email=%s&interest=%s">Unsubscribe</a></br>' % (email, email, interest)	
		message.add_attachment(html_content, subtype="html")

		server.send_message(message)
		
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

@app.route("/tweetquotebyid/<id>")
def tweetquotebyid(id):
	quote, author = elasticsearch_access.get_a_quote_and_author_by_id(id)
	twitterbot.tweet_quote(quote, author, None)
	return render_template('echo.html', text="A quote (id=%s) tweeted!" % id )

@app.route("/tweetquote")
def tweetquote():
	quote, author, tweet_id = elasticsearch_access.get_a_random_quote_and_author()
	twitterbot.tweet_quote(quote, author, None)
	'''	#Reteet previous quotes, no longer necessary
	quote2, author2, tweet_id2 = elasticsearch_access.get_a_random_quote_and_author()
	if tweet_id :
		twitterbot.tweet_quote(quote, author, tweet_id)
	else:
		twitterbot.tweet_quote(quote2, author2, tweet_id2)	
	'''
	return render_template('echo.html', text="A quote tweeted!")

@app.route("/tweetbookishfact")
def tweetbookishfact():
	fact,image = elasticsearch_access.get_a_random_fact()	
	if image == None:
		twitterbot.tweet(fact)
	else:
		twitterbot.tweet_with_media(fact, "static/facts/" + image)
	return render_template('echo.html', text="A bookish fact is tweeted!")

@app.route("/tweetbook")
def tweetbook():
	book_title, book_author, book_year, image, tweet_id = elasticsearch_access.get_a_random_book_with_detail()
	text = "Book Recommendation: " + book_title + " by " + book_author# + "\n" + "https://twitter.com/tothemax2050/status/" + tweet_id
	if image == None:
		twitterbot.tweet(text)
	else:
		twitterbot.tweet_with_media(text, "static/books/" + image)
	return render_template('echo.html', text="A book recommendation tweeted!")

@app.route("/retweetbook")
def retweetbook():
	tweet_id = elasticsearch_access.get_a_random_book_tweet_id()
	twitterbot.retweet_book(tweet_id)
	return render_template('echo.html', text="A book retweeted!")

@app.route("/retweet/<tweet_id>")
def retweet(tweet_id):
	twitterbot.retweet_book(tweet_id)
	return render_template('echo.html', text="retweeted!")

@app.route("/copy/<id>", methods=['POST'])
def copy(id):
	copy_paste_text = request.form['CopyText']
	elasticsearch_access.global_copy(id, copy_paste_text)
	url_with_id = '/cp/%s' % (id)
	return redirect(url_with_id)

@app.route("/copypaste/<i>")
@app.route("/cp/<i>")
def copypaste(i):
	copy_paste_text = elasticsearch_access.global_paste(i)
	actionstr='/copy/' + i
	return render_template('copypaste.html', id=i, actionstr=actionstr,text=copy_paste_text)

@app.route("/tf")
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

@app.route("/jn")
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

'''
@app.route("/generatelikesinbooklist")
def generatelikesinbooklist():
	elasticsearch_access.generate_likes_in_booklist()
	return render_template('echo.html', text="generatelikesinbooklist completed")

#@app.route("/generatetwitterbooklist")
def generatetwitterbooklist():
	#delete the existing index,and create a new empty one
	elasticsearch_access.delete_twitter_book_index()
	elasticsearch_access.create_twitter_book_index()
	#populate data
	allbooks, count = elasticsearch_access.get_all_twitter_books_from_booklist()
	for num, doc in enumerate(allbooks):
		title = doc["_source"]["Book Title"]
		tweet_id = doc["_source"]["TweetID"]
		like_count = twitterbot.get_likes(tweet_id)
		nonfiction = ( doc["_source"]["Genre"] != "Fiction" )
		id = doc["_source"]["id"]
		#write to ES
		elasticsearch_access.add_a_twitter_book(title,tweet_id,like_count,nonfiction,id)
	return render_template('echo.html', text="generatetwitterbooklist completed")
'''
@app.route("/photo")
def photo():
	photolist = elasticsearch_access.get_all_photos()
	return render_template('photo.html', photolist=photolist, photocount=len(photolist))

#liveathousandlives()
#generatetwitterbooklist()

if __name__ == '__main__':
	app.run(port=5000,debug=False)
	#app.run(host='0.0.0.0',port=80)
