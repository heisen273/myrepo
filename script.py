import sys
import time
import datetime
import requests
import unicodedata
import nltk
import operator
import mysql.connector
from boilerpipe.extract import Extractor
from langdetect import detect
from functools import reduce
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


#### when using boilerpipe extractors - is there any specific Extractor you prefer or I should use DefaultExtractor?

#### when we extract content and check if keyword occurs in content body - should the check be case sensetive?

#### when we do this check, there are two approaches to do this:
    ## Sort the sentences by the number of occurence of the keyword
    ## Sort the sentences by the number of occurence of the keyword if this keyword occurs in sentence at least one time

#### mobile/desktop screenshots must be stored locally on machine, where the tool will be executed
    ## this means that DB will be just having a file path pointer to stored screenshot, correct?


#### check with Vincent, if we could simply detect language using first/last/random sentence, instead of whole content.
#query_url = 'https://www.googleapis.com/customsearch/v1?key=%s&cx=%s&q=%s' % (api_key,searchEngine_id,searchQuery)

# Global values

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  database="act"
)

cursor = mydb.cursor()


def process(filename):

    """
    Queries all keywords from given file using `getKeywordLinks` function.
    """

    display, mobileDriver, desktopDriver = initDrivers()

    with open(filename) as f:
        keywords = [x.strip() for x in f.readlines()]

    for keyword in keywords:
        allKeywordLinks = getKeywordLinks(keyword)

        for link in allKeywordLinks:
            storeContent(link, keyword)

        processFilteredContent(keyword, mobileDriver, desktopDriver)

    deinitDrivers(display, mobileDriver, desktopDriver)

def getKeywordLinks(keyword):
    """
        Fills  and returns `keywordLinks` list is full for certain keyword. . .
    """
    keywordLinks = []
    queryUrl = 'https://www.googleapis.com/customsearch/v1?start=11&key=%s&cx=%s&q=%s' % (api_key,searchEngine_id,keyword)
    resp = requests.get(queryUrl).json()
    keywordLinks += [x['link'] for x in resp['items']]
    nextPageIndex = 11
    while True:
        queryUrl = 'https://www.googleapis.com/customsearch/v1?key=%s&cx=%s&q=%s&start=%s' % (api_key,searchEngine_id,keyword,nextPageIndex)
        resp = requests.get(queryUrl).json()
        if 'items' not in resp:
            return keywordLinks
        keywordLinks += [x['link'] for x in resp['items']]
        print(keywordLinks)
        nextPageIndex += 10
        print(nextPageIndex)
        time.sleep(1)


def storeContent(link, keyword):
    """
    Gets link content using boilerpipe, checks if it is valid, sets the score and save's it to temporary DB table.
    """

    content = unicodedata.normalize("NFKD", Extractor(extractor='DefaultExtractor', url=link).getText()).split('\n')

    # Split content in sentences
    sentences = reduce(operator.add, [nltk.sent_tokenize(x) for x in content])
    bigSentences = [x for x in sentences if len(x.split(' ')) > 10]

    # If there are more than 10 sentences with at least 10 words
    if len(bigSentences) > 10:
        # need to check language - it needs to be everything but english
        # Language is being checked using all sentences

        lang = detect(' '.join(bigSentences)).upper()

        if lang != 'EN':

            # Calculate score
            contentScore = ' '.join(bigSentences).lower().count(keyword.lower())

            # Save to tmp table
            insertQuery = "INSERT INTO tmp_keywords (keyword, link, original, score, lang, process_date) VALUES (%s, %s, %s, %s, %s, %s)"
            insertValues = (keyword, link, ' '.join(bigSentences), contentScore, lang, datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
            cursor.execute(insertQuery, insertValues)
            mydb.commit()

def processFilteredContent(keyword, mobileDriver, desktopDriver):
    """ """

    topResultsQuery = "SELECT * FROM tmp_keywords WHERE keyword = %s AND score <> 0 ORDER BY score DESC LIMIT 5" %keyword
    cursor.execute(topResultsQuery)

    queryResult = cursor.fetchall()
    if len(queryResult) > 0:

        for item in queryResult:
            link = item[1]
            originalContent = item[2]
            score = item[3]
            lang = item[4]

            translatedContent = ' '.join([pydeepl.translate(x, 'EN', from_lang=lang) for x in nltk.sent_tokenize(originalContent)])
            mobilePath, desktopPath = getScreenshots(mobileDriver, desktopDriver)

            insertQuery = "INSERT INTO keywords (keyword, link, original, translation, desktop_screenshot, mobile_screenshot, score, original_lang, process_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            insertValues = (keyword, link, originalContent, translatedContent, score, mobilePath, desktopPath, lang, datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
            cursor.execute(insertQuery, insertValues)
            mydb.commit()


def getScreenshots(link, mobileDriver, desktopDriver):

    mobileDriver.get(link)
    mobilePath = sys.path[0] + '/screenshots/mobile/'+link+'.png'
    mobileDriver.save_screenshot(mobilePath)

    desktopDriver.get(link)
    desktopPath = sys.path[0] + '/screenshots/desktop/'+link+'.png'
    desktopDriver.save_screenshot(desktopPath)

    return mobilePath, desktopPath


def initDrivers():

    display = Display(visible=0)
    display.start()
    mobileOpts = Options()
    mobileOpts.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 12_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1")
    mobileDriver = webdriver.Chrome(executable_path='/usr/lib/chromium-browser/chromedriver', chrome_options=mobileOpts)

    desktopOpts = Options()
    desktopOpts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.1 Safari/605.1.15")
    desktopDriver = webdriver.Chrome(executable_path='/usr/lib/chromium-browser/chromedriver', chrome_options=desktopOpts)

    return display, mobileDriver, desktopDriver

def deinitDrivers(display, mobileDriver, desktopDriver):

    display.stop()
    mobileDriver.quit()
    desktopDriver.quit()



process('./keywords.csv')

        ## Sort the sentences by the number of occurence of the keyword
        #sorted([(x,x.count('iphone')) for x in bigSentences ], key=lambda x: x[1])

        ## Sort the sentences by the number of occurence of the keyword if this keyword occurs in sentence at least one time
        #sorted([(x,x.count('iphone')) for x in bigSentences if x.count('iphone')>0 ], key=lambda x: x[1])
        #sortedSentences = [x[0] for x in sorted([(x,x.count(keyword)) for x in bigSentences if x.count(keyword)>0 ], key=lambda x: x[1], reverse=True)]
        # Sort the sentences by the number of occurence of the keyword