import json
import os.path, time


def stat():
    print(os.path.getmtime("photos.json"))
    print(os.path.getmtime("photos2.json"))
    if os.path.getmtime("photos2.json") > os.path.getmtime("photos.json"):
        new_file = "photos2.json"
    else:
        new_file = "photos.json"
    
    file2 = "quotes.json"
    file3 = "words.json"
    file4 = "notes.json"

    with open(new_file, "r") as new_file_hdl:
        print("stat on %s" % (new_file))
        photo_dict = json.load(new_file_hdl)

    with open(file2, "r") as file2_hdl:
        print("stat on %s" % (file2))
        dict2 = json.load(file2_hdl)

    with open(file3, "r") as file3_hdl:
        print("stat on %s" % (file3))
        dict3 = json.load(file3_hdl)

    with open(file4, "r") as file4_hdl:
        print("stat on %s" % (file4))
        dict4 = json.load(file4_hdl)

    dict2.update(photo_dict)
    dict3.update(dict2)
    dict4.update(dict3)
    return(dict4)

def add_photo(filepath):

    #photo_data is a dict
    #photo_list is an array
    photo_list = []

    print(os.path.getmtime("photos.json"))
    print(os.path.getmtime("photos2.json"))
    print("photos.json Last modified: %s" % time.ctime(os.path.getmtime("photos.json")))
    print("photos2.json Last modified: %s" % time.ctime(os.path.getmtime("photos2.json")))

    if os.path.getmtime("photos2.json") > os.path.getmtime("photos.json"):
        new_file = "photos2.json"
        old_file = "photos.json"
    else:
        new_file = "photos.json"
        old_file = "photos2.json"

    with open(old_file, "w") as old_file_hdl:
        with open(new_file, "r") as new_file_hdl:
            #always operate on the newer file
            print("operate on %s, write to %s" % (new_file, old_file))
            photo_dict = json.load(new_file_hdl)
            print("photo_dict:\n", photo_dict)
            photo_list = photo_dict["photos"] 
            print("photo_list_len:\n", len(photo_list))
            photo_count = photo_dict["photo_count"]
            print("photo_count: ", photo_count)
            entry_new = {'index':photo_count,'filepath':filepath}
            photo_list.append(entry_new)
            photo_dict["photo_count"] = photo_count+1
            print(photo_dict)
            json.dump(photo_dict, old_file_hdl, indent = 4)

    #backup the file
    cp_cmd = 'cp "%s" "%s"' % (old_file, "photos_backup.json")
    os.system(cp_cmd)

import random
def get_a_random_photo() :

    json_file = "photos.json"
    with open(json_file, "r") as file_hdl:
        photo_dict = json.load(file_hdl)
        print("photo_dict:\n", photo_dict)
        photo_list = photo_dict["photos"] 
        print("photo_list_len:\n", len(photo_list))
        photo_count = photo_dict["photo_count"]
        print("photo_count: ", photo_count)
        random_index = random.randint(0,photo_count-1)
        print("random_index: ", random_index)
        random_photo_dict = photo_list[random_index]
        return(random_photo_dict["filepath"])

def get_a_random_quote() :

    json_file = "quotes.json"
    with open(json_file, "r") as file_hdl:
        quote_dict = json.load(file_hdl)
        quote_list = quote_dict["quotes"] 
        print("quote_list_len:\n", len(quote_list))
        quote_count = quote_dict["quote_count"]
        random_index = random.randint(0,quote_count-1)
        print("random_index: ", random_index)
        random_dict = quote_list[random_index]
        return(random_dict["text"] + "  By " + random_dict["author"])


def get_a_random_word() :

    json_file = "words.json"
    with open(json_file, "r") as file_hdl:
        word_dict = json.load(file_hdl)
        word_list = word_dict["words"] 
        print("word_list_len:\n", len(word_list))
        word_count = word_dict["word_count"]
        random_index = random.randint(0,word_count-1)
        print("random_index: ", random_index)
        random_dict = word_list[random_index]
        return(random_dict["word"] + ": " + random_dict["definition"] + ".  " + random_dict["sentences"])

def upload_a_quote(text, author):

    #quote_data is a dict
    #quote_list is an array
    quote_list = []
    quote_file = "quotes.json"
    quote_backup_file = "quotes_backup.json"

    with open(quote_file, "r+") as file_hdl:
        print("operate on %s" % (quote_file))
        quote_dict = json.load(file_hdl)
        print("quote_dict:\n", quote_dict)
        quote_list = quote_dict["quotes"] 
        print("quote_list_len:\n", len(quote_list))
        quote_count = quote_dict["quote_count"]
        print("quote_count: ", quote_count)
        entry_new = {'index':quote_count,'text':text,'author':author}
        quote_list.append(entry_new)
        quote_dict["quote_count"] = quote_count+1
        print(quote_dict)
        file_hdl.seek(0)
        json.dump(quote_dict, file_hdl, indent = 4)

    #backup the file
    cp_cmd = 'cp "%s" "%s"' % (quote_file, quote_backup_file)
    os.system(cp_cmd)



def upload_a_word(word, definition, sentences):

    #quote_data is a dict
    #quote_list is an array
    word_list = []
    word_file = "words.json"
    word_backup_file = "words_backup.json"

    with open(word_file, "r+") as file_hdl:
        print("operate on %s" % (word_file))
        word_dict = json.load(file_hdl)
        print("word_dict:\n", word_dict)
        word_list = word_dict["words"] 
        print("word_list_len:\n", len(word_list))
        word_count = word_dict["word_count"]
        print("word_count: ", word_count)
        entry_new = {'index':word_count,'word':word,'definition':definition,'sentences':sentences}
        word_list.append(entry_new)
        word_dict["word_count"] = word_count+1
        print(word_dict)
        file_hdl.seek(0)
        json.dump(word_dict, file_hdl, indent = 4)

    #backup the file
    cp_cmd = 'cp "%s" "%s"' % (word_file, word_backup_file)
    os.system(cp_cmd)


def upload_a_note(label, text):

    note_list = []
    note_file = "notes.json"
    note_backup_file = "notes_backup.json"

    with open(note_file, "r+") as file_hdl:
        print("operate on %s" % (note_file))
        note_dict = json.load(file_hdl)
        print("note_dict:\n", note_dict)
        note_list = note_dict["notes"] 
        print("note_list_len:\n", len(note_list))
        note_count = note_dict["note_count"]
        print("note_count: ", note_count)
        entry_new = {'index':note_count,'label':label,'text':text}
        note_list.append(entry_new)
        note_dict["note_count"] = note_count+1
        print(note_dict)
        file_hdl.seek(0)
        json.dump(note_dict, file_hdl, indent = 4)

    #backup the file
    cp_cmd = 'cp "%s" "%s"' % (note_file, note_backup_file)
    os.system(cp_cmd)

def save_plot_data(x,y):

    plot_file = "plot.json"
    plot_backup_file = "plot_backup.json"

    plot_dict = {
        "x":x,
        "y":y
    }

    with open(plot_file, "r+") as file_hdl:
        print("operate on %s" % (plot_file))
        json.dump(plot_dict, file_hdl, indent = 4)

    #backup the file
    cp_cmd = 'cp "%s" "%s"' % (plot_file, plot_backup_file)
    os.system(cp_cmd)    