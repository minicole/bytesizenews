from django.conf import settings
from ByteSizeNews.DataAccessManagement import *
import pytz
import dateutil.parser
from datetime import datetime
import requests
import urllib.parse
import logging



log = logging.getLogger('django')


article_api_request_format = "https://newsapi.org/v1/articles?source={0}&sortBy={1}&apiKey={2}"
source_api_request_format = "https://newsapi.org/v1/sources?language={0}&category={1}&country={2}"
entity_extraction_format = "https://api.dandelion.eu/datatxt/nex/v1/?url={0}&include=types%2Ccategories&token={1}"
classify_api_format = "https://api.uclassify.com/v1/uclassify/topics/Classify?readkey={0}&text={1}"
all_source_api_request = "https://newsapi.org/v1/sources?language=en"
# Order to go through for sorts as available
available_sorts = ["latest", "popular", "top"]

CURRENT_SOURCE_BLACKLIST_BY_SOURCE_ID = ['associated-press', 'breitbart-news', 'reddit-r-all',
                                         'hacker-news', 'business-insider-uk', 'buzzfeed',
                                         'espn-cric-info', 'football-italia', 'mtv-news-uk', 'four-four-two',
                                         'mashable', 'metro', 'mirror', 'the-lad-bible', 'the-sport-bible',
                                         'the-times-of-india']

def fetch_and_save_latest_news():
    """
    Fetch all new news articles, sorted by latest sort if available, otherwise popular then top
    :return: 
    """
    # Only want english now
    all_sources = Source.objects.filter(language="en")

    for source in all_sources:
        # ignore all articles from blacklisted sources
        if source.source_id in CURRENT_SOURCE_BLACKLIST_BY_SOURCE_ID:
            continue
        fetch_latest_news_by_source(source)



def fetch_latest_news_by_source(source):
    """
    fetch article from newsapi service for specified source
    :param source: Source object
    :return: 
    """
    sortBy = available_sorts[0]
    for available_sort in available_sorts:
        if available_sort in source.sortBysAvailable:
            sortBy = available_sort
            break

    apirequest = article_api_request_format.format(source.source_id, sortBy, settings.NEWS_KEY)
    r = requests.get(apirequest)
    jsonresponse = r.json()
    if jsonresponse['status'] == "ok":
        articles = jsonresponse['articles']# gives array of latest articles

        for article in articles:
            try:
                publishedDate = dateutil.parser.parse(article['publishedAt'])
            except:
                # Put current
                publishedDate = datetime.now(pytz.utc)

            #Call the Dandelion API to get entity text for original char count + category via uclassify
            entityRequest = entity_extraction_format.format(article['url'], settings.DANDELION_KEY)
            log.info(entityRequest)
            entityResponse = requests.get(entityRequest)

            jsonEntityRepsonse = entityResponse.json()
            log.info(jsonEntityRepsonse)
            originalCharCount = 0
            if 'text' in jsonEntityRepsonse:
                unsummarized_text = jsonEntityRepsonse['text']
                originalCharCount = len(unsummarized_text)

                # get category
                try:
                    urlencodedText = urllib.parse.quote_plus(unsummarized_text)
                    classifyRequest = classify_api_format.format(settings.UCLASSIFY_KEY, urlencodedText)
                    log.info(classifyRequest)
                    classifyResponse = requests.get(classifyRequest)
                    jsonClassifyResponse = classifyResponse.json()
                    log.info(jsonClassifyResponse)
                    max_key_val = 0
                    category = "General"
                    for key in jsonClassifyResponse:
                        if jsonClassifyResponse[key] > max_key_val:
                            max_key_val = jsonClassifyResponse[key]
                            category = key

                except:
                    category = "General"

            save_article_unsummarized(title=article['title'], author=article['author'], url=article['url'], source=source,
                                      description=article['description'], url_to_image=article['urlToImage'],
                                      published_at=publishedDate, nb_original_chars=originalCharCount, category=category)
            # #Ony save once per call
            # if DEBUG:
            #     log.info(article)
            #     break


def fetch_save_and_update_sources():
    apirequest = all_source_api_request
    getResponse = requests.get(apirequest)
    jsonresponse = getResponse.json()

    if jsonresponse['status'] == "ok":
        sources = jsonresponse['sources']

        for source in sources:
            logo_url_list = [source['urlsToLogos']['large'], source['urlsToLogos']['medium'],
                             source['urlsToLogos']['small']]

            save_source(source['id'], source['category'], source['name'], source['description'], source['language'],
                        source['country'], source['sortBysAvailable'], logo_url_list)


