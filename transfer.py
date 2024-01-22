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
#sender_email = "max.readingisalifestyle@gmail.com"
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
	
	fact, fact_image = elasticsearch_access.get_a_random_fact()

	sub_count = elasticsearch_access.get_subscriber_count()
	return render_template('index.html',word=random_word,quote=random_quote,photolink=photo_id,photomedia=insta_id,
		book=random_book,book_image=book_image,email=email,sub_count=sub_count,fact=fact,fact_image=fact_image)

@app.route("/tweetdailybookishquestion")
def tweetdailybookishquestion():
	
	question_list = [
		#Monday: weekend wrap-up
		[
			"Have you finished a book over the weekend?",
			"How was your bookish weekend?",
			"Did your weekend go according to the reading plan?",
			"How many hours (or pages) did you read last weekend?",
			"What's a bookish thing you did last weekend?",
		],
		#Tuesday: book properties
		[
			"What genre is your current read?",
			"Post a GIF/Image that best describes your emotional state with your current read!",
			"Use one word to describe your current read!",
			"Where are you being transported to by your current read?",
			"What's the main message of your current read?",
			"Describe the book you're currently reading in five words or fewer!",
			"Describe your current read with only emojis!",

		],
		#Wednesday: character
		[
			"Name a woman character from your current read!",
			"Off the top of your head, could you name a fictional book character?",
			"What's the age of the main character from your current read?",
			"Name two characters from the book you’re currently reading!",
			"What is the job of the main character from your current read?",
			"Which character from your current read would you like to meet?",
			"Who's the MC in your current read?",
			"Name a nonhuman character from your current read?",
			"What's a character from your current read that you want to befriend?",
			"Name a supporting character in your current read!",

		],
		#Thursday
		[
			"How did you like the book you just finished?",
			"Share a quote from your current read!",
			"Describe a scene from the book you’re currently reading!"
		],
		#Friday
		[
			"What are you planning on reading this weekend?"
		],
		#Saturday: Author
		[
			"If you could spend a day with an author, who would you spend it with?",
			"Who is your new favorite author?",
			"If you could interview one author, living or dead, who would it be and what would you ask?",
			"Which author is on your mind right now?",
			"Who's the last author that made you cry, or tear up?",
			"If you could bring one author back from the dead, who would it be?"
		],
		#Sunday
		[
			"Any thoughts on your current read?",
			"What have you learned so far from your current read?"
		]
	]
	
	dt = datetime.now()
	i = dt.weekday()
	q_num = len(question_list[i])

	question = question_list[i][random.randint(1,q_num) - 1]
	twitterbot.tweet(question)

	return render_template('echo.html', text="A daily bookish question is tweeted!")

@app.route('/privacy')
def privacy():
	return render_template('privacy.html')

@app.route('/apps')
def apps():
	return render_template('app.html')

@app.route('/echo_search')
def echo_search():
	return render_template('echo_search.html')

@app.route('/readingisalifestyle')
def readingisalifestyle():
	return render_template('index2.html')

@app.route('/<reader>')
def readers(reader):
		
	allbooks, count = elasticsearch_access.get_all_book_sorted_by_finished_date()
	items = [{}] * count
	oneitem = {}
	current_read_list = []
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
		oneitem["Date Finished"] = doc["Date Finished"]
		oneitem["Date Started"] = doc["Date Started"]
		#print(oneitem)
		items[num] = oneitem.copy()  #use copy() or deepcopy instead of assigning dict directly, which copes reference not value

		if( doc["Date Finished"] == "4/15/1976" and doc["Date Started"] != None ):
			current_read_list.append(oneitem.copy())
			print("current_list: ", oneitem)

	print("current list count: ",len(current_read_list))
	#print(current_read_list)

	return render_template('readers.html', reader=reader, items=items, count=count, current_read_list=current_read_list, current_read_count=len(current_read_list))

@app.route('/lfl')
@app.route('/littlefreelibrary')
def littlefreelibrary():
	lflbooklist = ["IMG_1672.jpg","IMG_1673.jpg","IMG_1674.jpeg",\
				"IMG_1739.jpg","IMG_1741.jpg","IMG_1742.jpg","IMG_1743.jpg","IMG_1744.jpg","IMG_1745.jpg","IMG_1746.jpeg"]
	return render_template('littlefreelibrary.html', lflbooklist=lflbooklist, lflbooklistcount=len(lflbooklist))

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

	#elasticsearch_access.apittracking_increment_callcount("getquote")

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
	#elasticsearch_access.apittracking_increment_callcount("getbook")
	book_title, book_author, book_year, book_image, rating = elasticsearch_access.get_a_random_book_rec_with_detail()
	dict = {
        "title": book_title,
        "author": book_author,
		"year": book_year,
		"image": book_image,
		"rating": rating
	}
	#Dictionary to JSON Object
	return json.dumps(dict)

#api - v1 - fact & [image]
@app.route("/api/getfact")
def getfact():
	fact,image = elasticsearch_access.get_a_random_fact()
	dict = {
        "fact": fact,
		"image": image
	}
	#Dictionary to JSON Object
	return json.dumps(dict)

#test
#quote_ret = getbook()

#api - v1 - photo
@app.route("/api/getphoto")
def getphoto():
	#elasticsearch_access.apittracking_increment_callcount("getphoto")
	image_name, media = elasticsearch_access.get_a_random_photo()
	dict = {
        "image": image_name + ".jpg"
	}
	#Dictionary to JSON Object
	return json.dumps(dict)

#test
#quote_ret = getbook()

#api - v1 - get booksih question
@app.route("/api/getquestion")
def getquestioin():
	arg_count = len(request.args)
	arg_cat = request.args.get('cat')
	print("api/getquote", arg_count, arg_cat)

	if(arg_cat != None):
		question = elasticsearch_access.get_a_random_question_by_category(arg_cat)
	else:
		question = elasticsearch_access.get_a_random_question()

	dict = {
        "question": question
	}
	#Dictionary to JSON Object
	return json.dumps(dict)

@app.route("/api/getjphrase")
def getjphrase():
	arg_count = len(request.args)
	print("api/getjphrase", arg_count)

	jphrase = elasticsearch_access.get_a_random_jphrase()

	#dict = {
    #    "phrase": jphrase
	#}
	#Dictionary to JSON Object
	#return json.dumps(dict)
	
	return '<center><span style="font-size: 8vw;">%s</span></center>' % jphrase

@app.route("/bookishfacts")
def bookishfacts():
	arg_count = len(request.args)

	allrecords, count = elasticsearch_access.get_all_facts()

	fact, image = elasticsearch_access.get_a_random_fact()

	#count=10  #test
	items = [{}] * count
	oneitem = {}
	for num, doc in enumerate(allrecords):
		oneitem["Fact"] = doc["_source"]["Fact"]
		oneitem["Image"] = doc["_source"]["Image File Name"]
		#print(oneitem)
		items[num] = oneitem.copy()  #use copy() or deepcopy instead of assigning dict directly, which copes reference not value
	col_names=["Fact","Image"]
	col_width={
		'Fact':"90%",
		'Image':"10%"
	}
	return render_template('fact.html', col_names=col_names, col_width=col_width, items=items, count=count, fact=fact, fact_image=image)

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
		oneitem["Date Finished"] = doc["Date Finished"]
		#print(oneitem)
		items[num] = oneitem.copy()  #use copy() or deepcopy instead of assigning dict directly, which copes reference not value
		items_sorted[num] = oneitem.copy()  #use copy() or deepcopy instead of assigning dict directly, which copes reference not value

		if (doc["TweetID"] != None ):
			twitter_booklist.append(oneitem["ID"])
			if ( doc["Genre"] != "Fiction" ):
				twitter_booklist_nonfiction.append(oneitem["ID"])

	#Prepare the sorted list in python instead javascript because js does not easier provide an easy for deep copy of the original list 
	#items_sorted.sort(key=itemgetter('Book Title')) 
	
	#Sort by "Date Finished"
	items_sorted.sort(key=lambda x: datetime.strptime(x["Date Finished"],'%m/%d/%Y'), reverse=True)

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
	elasticsearch_access.add_a_subscription(email)
	email_notify_me("Newsletter - New subscription!", ("from: %s" % (email)))
	return render_template('echo.html', text="Thanks for your subscription!")

@app.route("/unsubscribe")
def unsubscribe():

	arg_count = len(request.args)
	email = request.args.get('email')
	if email == None:
		email = "..."
	return render_template('unsubscribe.html', email=email)

@app.route("/unsubscribing", methods=['POST'])
def unsubscribing():
	email = request.form['email']
	print("unsubscribe %s" % (email))
	elasticsearch_access.remove_a_subscription(email)
	email_notify_me("Newsletter - Unsubscription", ("from: %s" % (email)))
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

	#doc_word = elasticsearch_access.get_a_random_word()
	#random_word = doc_word["Word"] + ": " + doc_word["Definition"] + ".  " + doc_word["Example Sentences"]
	
	fact, fact_image = elasticsearch_access.get_a_random_fact()

	book_title, book_author, book_year, book_image, rating = elasticsearch_access.get_a_random_book_rec_with_detail()
	
	photo_id, insta_id = elasticsearch_access.get_a_random_photo()

	question = elasticsearch_access.get_a_random_question()

	newsletter_prefix = "Welcome to Reading Is A Lifesytle Daily Newsletter!\n"

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

		#for testing, only send to my personal email
		if TESTING_NEWSLETTER == True:
			email = myemail

		print("newsletter, Loop_count = %d, email = %s" % (num,email) )

		del message['To']
		del message['Subject']

		message['To'] = email
		#WARNING!!! DO NOT SENT DEBUGGING MSG TO CUSTOMERS!!!
		message['Subject'] = "Reading Is A Lifestyle — Daily Newsletter"
	
		#set content and attachment
		message.clear_content()
		#message.set_content(newsletter_content)	

		html_content_book = "<br><b>Book Recommendation</b><br>&nbsp;&nbsp;&nbsp;&nbsp;Title: %s<br>&nbsp;&nbsp;&nbsp;&nbsp;Author: %s<br>&nbsp;&nbsp;&nbsp;&nbsp;Year Published: %s<br>&nbsp;&nbsp;&nbsp;&nbsp;" % (book_title, book_author, book_year)
		if( book_image ):
			book_url = "https://readingisalifestyle.com/static/books/%s" % book_image
			html_content_book += '<img src="%s" alt="Book of the Day" style="width:50%%;height:auto;"><br>' % book_url
		message.add_attachment(html_content_book, subtype="html")

		html_content_fact = "<br><b>Bookish Fact</b><br>&nbsp;&nbsp;&nbsp;&nbsp;%s<br>&nbsp;&nbsp;&nbsp;&nbsp;" % (fact)
		if( fact_image ):
			book_url = "https://readingisalifestyle.com/static/facts/%s" % fact_image
			html_content_fact += '<img src="%s" alt="Bookish Fact" style="width:25%%;height:auto;"><br>' % book_url
		message.add_attachment(html_content_fact, subtype="html")

		html_content_quote = "<br><b>Inspirational Quote</b><br>&nbsp;&nbsp;&nbsp;&nbsp;%s&nbsp;—%s<br>" % (quote, author)
		message.add_attachment(html_content_quote, subtype="html")

		html_content_photo = "<br><b>Photo of the Day</b><br>&nbsp;&nbsp;&nbsp;&nbsp;"
		image_url = "https://readingisalifestyle.com/static/instagram/%s.jpg" % photo_id
		html_content_photo += '<img src="%s" alt="Photo of the Day" style="width:50%%;height:auto;"><br>' % image_url
		message.add_attachment(html_content_photo, subtype="html")

		html_content_question = "<br><b>A Bookish Question For You</b><br>&nbsp;&nbsp;&nbsp;&nbsp;%s<br>" % (question)
		message.add_attachment(html_content_question, subtype="html")

		html_content = "<br><br>---------------------------------------<br>Visit our website: https://readingisalifestyle.com"
		html_content += '<br><a href="https://readingisalifestyle.com/#sub">Subscribe</a>&nbsp;|&nbsp;'
		html_content += '<a href="https://readingisalifestyle.com/unsubscribe?email=%s">Unsubscribe</a></br>' % (email)	
		message.add_attachment(html_content, subtype="html")

		server.send_message(message)

		if TESTING_NEWSLETTER == True:
			break;
		
	server.quit()
	email_notify_me("Newsletter sent!", "")

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
	book_title, book_author, book_year, image, rating = elasticsearch_access.get_a_random_book_rec_with_detail()
	text = "Book Recommendation: " + book_title + " by " + book_author		
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

#if __name__ == '__main__':
	#app.run(port=5000,debug=False)
	#app.run(host='0.0.0.0',port=80)
