from bs4 import BeautifulSoup, SoupStrainer
import re #regex
import requests
import json
import urllib.request
import pandas as pd
import numpy as np
from selenium import webdriver
import pymongo
from pymongo import MongoClient
from time import sleep
import random
from datetime import date
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By

# Open URL
# list_url = ['https://tiki.vn/cac-mon-the-thao-choi-vot/c8411','https://tiki.vn/trang-phuc-the-thao-nu/c6141',
#             'https://tiki.vn/the-thao-da-ngoai/c1975','https://tiki.vn/dung-cu-thiet-bi-tap-the-thao/c24128',
#             'https://tiki.vn/dien-tu-dien-lanh/c4221','https://tiki.vn/may-giat/c3862',
#             'https://tiki.vn/may-lanh-may-dieu-hoa/c3865','https://tiki.vn/tivi/c5015',
#             'https://tiki.vn/thoi-trang-nam/c915','https://tiki.vn/ao-so-mi-nam/c918']
list_url = ['https://tiki.vn/nha-cua-doi-song/c1883','https://tiki.vn/tui-thoi-trang-nam/c27616',
            'https://tiki.vn/phu-kien-thoi-trang/c27498','https://tiki.vn/nha-sach-tiki/c8322',
            'https://tiki.vn/sach-truyen-tieng-viet/c316','https://tiki.vn/sach-van-hoc/c839']
links = []
driver = webdriver.Chrome('chromedriver.exe')
for url in list_url:
    driver.get(url)
    sleep(random.randint(5,10))
    elems = driver.find_elements(By.CSS_SELECTOR , ".product-item")
    for elem in elems:
        links.append(elem.get_attribute('href'))

sleep(random.randint(5,7))
def get_comment(link):
    list_review = []
    for i in link:
        driver.get(i)
        sleep(2)
        driver.execute_script("window.scrollTo(0,  window.scrollY + 2500);")
        sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(3)
        e = driver.find_elements(By.CSS_SELECTOR , ".review-comment__content")
        for elem in e:
            list_review.append(elem.text)
    return list_review

def standardize_data(row):
    # remove stopword
    # Remove . ? , at index final
    row = re.sub(r"[\.,\?]+$-", "", row)
    # Remove all . , " ... in sentences
    row = row.replace(",", " ").replace(".", " ") \
        .replace(";", " ").replace("“", " ") \
        .replace(":", " ").replace("”", " ") \
        .replace('"', " ").replace("'", " ") \
        .replace("!", " ").replace("?", " ") \
        .replace("-", " ").replace("?", " ")

    row = row.strip()
    return row
def std_comment(comments):
    list_std_comment = []
    for item in comments:
        list_std_comment.append(standardize_data(item))
    return list_std_comment


list_comment = get_comment(links)
list_comment = std_comment(list_comment)

driver.close()

#connect to mongo atlas 
client = MongoClient('mongodb+srv://hieudt:77223508@atlascluster.twqbhkg.mongodb.net/test')
db = client["DataLake"]
collection = db["Collection"]

comments = []
for i in range(list_comment):
    comment = {"_id": i+1, "comment": list_comment[i],'date': str(date.today())}

#insert data
collection.insert_many(comments)



# df = pd.DataFrame()
# df['Comment'] = list_comment
# df.to_excel('dataCommentTiki_3.xlsx')

    
