import pandas as pd 
import numpy as np
import re #regex
import pandas as pd
import joblib #load, dump pkl
from nltk import ngrams
from underthesea import word_tokenize

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

# # scrap comment = selenium
from selenium import webdriver 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import random

from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from werkzeug.utils import secure_filename

import pickle
from keras.models import load_model


app = Flask(__name__)


def standardize_data(row):
    # remove stopword
    # Remove . ? , at index final
    row = re.sub(r"[\.,\?]+$", "", row)
    # Remove all . , " ... in sentences
    row = row.replace(",", " ").replace(".", " ") \
        .replace(";", " ").replace("“", " ") \
        .replace(":", " ").replace("”", " ") \
        .replace('"', " ").replace("'", " ") \
        .replace("!", " ").replace("?", " ") \
        .replace("-", " ").replace("?", " ")

    row = row.strip()
    return row

def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)

def tokenizer_(row):
    return word_tokenize(row, format="text")




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/',methods=['POST','GET'])
def upload_Text():
    if 'text' not in request.form:
        return redirect(request.url)
    url = request.form['text']
    driver = webdriver.Chrome('chromedriver.exe')
    driver.get(url)
    sleep(random.randint(5,10))
    sleep(2)
    driver.execute_script("window.scrollTo(0,  window.scrollY + 2500);")
    sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(3)
    e = driver.find_elements(By.CSS_SELECTOR , ".review-comment__content")
    list_review = []
    for elem in e:
        list_review.append(elem.text)
    
    # if url is not None:
    #     return render_template('index.html',list_review = list_review)

    df = pd.DataFrame()
    df['Comment'] = list_review

    df['Comment'] = df['Comment'].apply(str)
    df['Comment'] = df['Comment'].apply(standardize_data)
    df['Comment'] = df['Comment'].apply(deEmojify)  
    df['Comment'] = df['Comment'].apply(tokenizer_)

    with open('tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)
    model = load_model('chechpoint.h5')
    data_test = tokenizer.texts_to_sequences(df['Comment'])
    data_test = pad_sequences(data_test,maxlen=148,truncating='post',padding='post')
    results = model.predict(data_test)
    results = list(results)
    reviews = []
    good , bad = 0,0
    for i in results:
        if i > 0.5:
            bad += 1
            reviews.append('Bad')
        else:
            good += 1
            reviews.append("Good")

    r = zip(list(df['Comment']),reviews)
    if good > bad:
        message = "Sản phẩm này quý khách lên mua nhé"
    else:
        message = "Sản phẩm này quý khách không lên mua nhé"
    if url is not None:
         return render_template('index.html',r = r ,message = message)

if __name__=='__main__':
    app.run(port=9050,debug=True)

