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



#### when using boilerpipe extractors - is there any specific Extractor you prefer or I should use DefaultExtractor?

#### when we extract content and check if keyword occurs in content body - should the check be case sensetive?

#### when we do this check, there are two approaches to do this:
    ## Sort the sentences by the number of occurence of the keyword
    ## Sort the sentences by the number of occurence of the keyword if this keyword occurs in sentence at least one time

#### mobile/desktop screenshots must be stored locally on machine, where the tool will be executed
    ## this means that DB will be just having a file path pointer to stored screenshot, correct?
####
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

    with open(filename) as f:
        keywords = [x.strip() for x in f.readlines()]

    for keyword in keywords:
        allKeywordLinks = getKeywordLinks(keyword)

        for link in allKeywordLinks:
            storeContent(link, keyword)

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
        ## check with Vincent, if we could simply detect language using first/last/random sentence, instead of whole content.
        lang = detect(' '.join(bigSentences)).upper()

        if lang != 'EN':

            # Calculate score
            contentScore = ' '.join(bigSentences).lower().count(keyword.lower())

            # Save to tmp table
            insertQuery = "INSERT INTO tmp_keywords (keyword, link, original, score, process_date) VALUES (%s, %s, %s, %s, %s)"
            insertValues = (keyword, link, ' '.join(bigSentences), contentScore, datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
            cursor.execute(insertQuery, insertValues)
            mydb.commit()

def processFilteredContent(keyword):
    """ """

    topResultsQuery = "SELECT * FROM tmp_keywords "



process('./keywords.csv')

        ## Sort the sentences by the number of occurence of the keyword
        #sorted([(x,x.count('iphone')) for x in bigSentences ], key=lambda x: x[1])

        ## Sort the sentences by the number of occurence of the keyword if this keyword occurs in sentence at least one time
        #sorted([(x,x.count('iphone')) for x in bigSentences if x.count('iphone')>0 ], key=lambda x: x[1])
        #sortedSentences = [x[0] for x in sorted([(x,x.count(keyword)) for x in bigSentences if x.count(keyword)>0 ], key=lambda x: x[1], reverse=True)]
        # Sort the sentences by the number of occurence of the keyword

        #translatedContent = [pydeepl.translate(x, 'EN', from_lang=set([detect(x) for x in bigSentences]).pop().upper()) for x in bigSentences]