from django.conf import settings
from ByteSizeNews.DataAccessManagement import *
import pytz
import dateutil.parser
import requests
import logging


log = logging.getLogger(__name__)


DEBUG = True;
apirequestheader ="https://newsapi.org/v1/articles?source={0}&sortBy=latest&apiKey={1}"

    # "author": "TNW Deals",
    # "title": "Learn to tackle any task with project management training - only $69",
    # "description": "Learn the art of project management. Across nine courses, you'll take a deep-dive into nine distinct project management training.",
    # "url": "https://thenextweb.com/offers/2017/04/08/learn-tackle-task-project-management-training-69/",
    # "urlToImage": "https://cdn3.tnwcdn.com/wp-content/blogs.dir/1/files/2017/04/4nhFNRE.jpg",
    # "publishedAt": "2017-04-07T12:46:15Z"

def fetch_latest_news(source="the-next-web"):
    """fetch article from newsapi service for specified source"""
    apirequest = apirequestheader.format(source,settings.NEWS_KEY)
    log.info(apirequest)
    r = requests.get(apirequest)
    jsonresponse = r.json()

    articles = jsonresponse['articles'] # gives array of latest articles

    for article in articles:
        try:
            publishedDate = dateutil.parser.parse(article['publishedAt'])
        except:
            # Put current
            publishedDate = datetime.now(pytz.utc)
        save_article_unsummarized(article['title'], article['author'], article['url'], "N/A",jsonresponse['source'], article['description'], article['urlToImage'], publishedDate)
        #Ony save once per call
        if DEBUG:
            log.info(article)
            break
