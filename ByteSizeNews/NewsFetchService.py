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
lateral_entity_extraction_format = "https://document-parser-api.lateral.io/?url={0}"
lateral_headers = {'content-type': 'application/json', 'subscription-key': settings.LATERAL_KEY}
classify_api_format = "https://api.uclassify.com/v1/uclassify/topics/Classify?readkey={0}&text={1}"
all_source_api_request = "https://newsapi.org/v1/sources?language=en"
# Order to go through for sorts as available
available_sorts = ["latest", "popular", "top"]

CURRENT_SOURCE_BLACKLIST_BY_SOURCE_ID = ['associated-press', 'breitbart-news', 'reddit-r-all',
                                         'hacker-news', 'business-insider-uk', 'buzzfeed',
                                         'espn-cric-info', 'football-italia', 'mtv-news-uk', 'four-four-two',
                                         'mashable', 'metro', 'mirror', 'the-lad-bible', 'the-sport-bible',
                                         'the-times-of-india']

CHAR_COUNT_THRESHOLD = 1000

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
    articleCount = 0

    sortBy = available_sorts[0]
    for available_sort in available_sorts:
        if available_sort in source.sortBysAvailable:
            sortBy = available_sort
            break

    category = "General"  # default category
    originalCharCount = 0  # Default char count

    apirequest = article_api_request_format.format(source.source_id, sortBy, settings.NEWS_KEY)
    r = requests.get(apirequest)
    jsonresponse = r.json()
    if jsonresponse['status'] == "ok":
        articles = jsonresponse['articles']  #gives array of latest articles

        for article in articles:

            if article_already_in_db(article['url']):
                continue

            try:
                publishedDate = dateutil.parser.parse(article['publishedAt'])
            except:
                # Put current
                publishedDate = datetime.now(pytz.utc)

            # Call the Dandelion API one after each other if one fails, call other to get entity text for original char count
            #
            # If both fail call the lateral one

            # Pass one
            entityExtraction = dandelion_entity_extraction(settings.DANDELION_KEY[0], article['url'])

            originalCharCount = entityExtraction['nb_original_chars']

            # Pass 2
            if originalCharCount == 0:
                entityExtraction = dandelion_entity_extraction(settings.DANDELION_KEY[1], article['url'])

                originalCharCount = entityExtraction['nb_original_chars']

            # Pass 3
            if originalCharCount == 0:
                entityExtraction = lateral_entity_extraction(article['url'])
                originalCharCount = entityExtraction['nb_original_chars']

            # Only save articles with more than threshold
            if originalCharCount < CHAR_COUNT_THRESHOLD:
                continue

            # get category
            try:
                urlencodedText = urllib.parse.quote_plus(entityExtraction['unsummarized_text'])

                # Two passes on classification
                classifyRequest = classify_api_format.format(settings.UCLASSIFY_KEY[0], urlencodedText)
                # print(classifyRequest)
                classifyResponse = requests.get(classifyRequest, verify=False)
                jsonClassifyResponse = classifyResponse.json()
                # log.info(jsonClassifyResponse)

                secondPass = False
                # Pass 2:
                if 'statusCode' in jsonClassifyResponse:
                    if jsonClassifyResponse['statusCode'] == 400:
                        classifyRequest = classify_api_format.format(settings.UCLASSIFY_KEY[1], urlencodedText)
                        classifyResponse = requests.get(classifyRequest, verify=False)
                        jsonClassifyResponse = classifyResponse.json()
                        # log.info(jsonClassifyResponse)
                        log.info("Failed to classify after one pass")
                        secondPass = True
                else:
                    log.info("Classified after one pass")

                # if fail,
                if 'statusCode' in jsonClassifyResponse:
                    if jsonClassifyResponse['statusCode'] == 400:
                        log.info("Failed to classify after two passes")
                else:
                    if secondPass:
                        log.info("Classified after two passes")
                    # Can finally categorize
                    max_key_val = 0

                    for key in jsonClassifyResponse:
                        if jsonClassifyResponse[key] > max_key_val:
                            max_key_val = jsonClassifyResponse[key]
                            category = key

            except:
                log.info("Error extracting entity or category")

            save_article_unsummarized(title=article['title'], author=article['author'], url=article['url'],
                                      source=source,description=article['description'],
                                      url_to_image=article['urlToImage'], published_at=publishedDate,
                                      nb_original_chars=originalCharCount, category=category,
                                      unsummarized_text=entityExtraction)
            articleCount += 1

    log.info("{0} Articles added from source:{1}".format(articleCount, str(source)))

def dandelion_entity_extraction(dKey, url):
    entityRequest = entity_extraction_format.format(url, dKey)
    entityResponse = requests.get(entityRequest)

    jsonEntityRepsonse = entityResponse.json()
    originalCharCount = 0
    unsummarized_text = ""
    if 'text' in jsonEntityRepsonse:
        unsummarized_text = jsonEntityRepsonse['text'].encode('ascii', 'ignore')
        originalCharCount = len(unsummarized_text)
        log.info("Dandelion API used to extract entity")
    else:
        log.info("Dandelion API failed to extract entity")
    return {'nb_original_chars': originalCharCount,
            'unsummarized_text': unsummarized_text}


def lateral_entity_extraction(url):
    entityRequest = lateral_entity_extraction_format.format(url)
    entityResponse = requests.get(entityRequest, headers=lateral_headers)

    jsonEntityRepsonse = entityResponse.json()
    originalCharCount = 0
    unsummarized_text = ""
    if 'body' in jsonEntityRepsonse:
        unsummarized_text = jsonEntityRepsonse['body'].encode('ascii', 'ignore').decode('ascii')
        originalCharCount = len(unsummarized_text)
        log.info("Lateral API used to extract entity")
    else:
        log.info("Lateral API failed to extract entity")

    return {'nb_original_chars': originalCharCount,
            'unsummarized_text': unsummarized_text}


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


def article_already_in_db(url):
    try:
        article = Article.objects.get(url=url)
        if article is not None:
            return True
        else:
            return False
    except Article.DoesNotExist:
        return False
