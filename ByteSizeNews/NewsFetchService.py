from django.conf import settings
from ByteSizeNews.DataAccessManagement import *
import pytz
import dateutil.parser
from datetime import datetime
import requests
import logging


log = logging.getLogger(__name__)


DEBUG = True
article_api_request_format = "https://newsapi.org/v1/articles?source={0}&sortBy={1}&apiKey={2}"
source_api_request_format = "https://newsapi.org/v1/sources?language={0}&category={1}&country={2}"
all_source_api_request = "https://newsapi.org/v1/sources"
# Order to go through for sorts as available
available_sorts = ["latest", "popular", "top"]



def fetch_and_save_latest_news():
    """
    Fetch all new news articles, sorted by latest sort if available, otherwise popular then top
    :return: 
    """
    all_sources = Source.objects.all()

    for source in all_sources:
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
    log.info(apirequest)
    r = requests.get(apirequest)
    jsonresponse = r.json()
    if jsonresponse['status'] == "ok":
        articles = jsonresponse['articles'] # gives array of latest articles

        for article in articles:
            try:
                publishedDate = dateutil.parser.parse(article['publishedAt'])
            except:
                # Put current
                publishedDate = datetime.now(pytz.utc)

            save_article_unsummarized(title=article['title'], author=article['author'], url=article['url'], source=source,
                                      description=article['description'], url_to_image=article['urlToImage'],
                                      published_at=publishedDate)
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


