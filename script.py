import time

public_url = 'https://cse.google.com/cse?cx=014289537967084031256:2dgojxdesig'
searchEngine_id = '014289537967084031256:2dgojxdesig'
api_key = 'AIzaSyAJo5ph7O9UeIR2gTe4Cd_dTnyYa9Tn2xA'


query_url = 'https://www.googleapis.com/customsearch/v1?key=%s&cx=%s&q=%s' % (api_key,searchEngine_id,searchQuery)

def pullKeywordLinks(filename):

    """ Function, that queries all keywords from given file and stores them to `keyword_links` list.
    Once `keywords_links` list is full for certain keyword. . .
    """

    with open(filename) as f:
        keywords = [x.strip() for x in f.readlines()]

    for keyword in keywords:
        keyword_links = []

        query_url = 'https://www.googleapis.com/customsearch/v1?start=11&key=%s&cx=%s&q=%s' % (api_key,searchEngine_id,keyword)

        resp = requests.get(query_url).json()
        keyword_links += [x['link'] for x in resp['items']]

        nextPageIndex = 11

        while True:
            query_url = 'https://www.googleapis.com/customsearch/v1?key=%s&cx=%s&q=%s&start=%s' % (api_key,searchEngine_id,keyword,nextPageIndex)
            resp = requests.get(query_url).json()
            if not resp.has_key('items'):
                break
            keyword_links += [x['link'] for x in resp['items']]
            print(keyword_links)
            nextPageIndex += 10
            print(nextPageIndex)
            time.sleep(1)




