from ByteSizeNews.models import *
from ByteSizeNews.SummarizeService import *
from ByteSizeNews.SentimentAnalysisService import *
from datetime import datetime, timedelta
from mongoengine.queryset.visitor import Q
import logging
import json

log = logging.getLogger('django')

TIME_THRESHOLD_CONSTANT_DAYS = 7
TIME_THRESHOLD_CONSTANT_HOURS = 0

DEFAULT_LANGUAGES_LIST = ["en"]

NB_ARTICLES_PER_PAGE = 30

UPDATE_SUMMARY_RATIO_THRESHOLD = 2.9


def get_articles(page):
    return get_articles_from_category("All", pageNumber=page)


def get_all_categories():
    categorieslist = Article.objects.distinct(field='category')

    #Only general available
    if len(categorieslist) < 2:
        categorieslist = Source.objects.distinct(field='category')
    # return ["business", "entertainment", "gaming", "general",
    #         "music", "politics", "science-and-nature", "sport", "technology"]
    return json.dumps({'categories': categorieslist})

def get_all_languages():
    return Source.objects.distinct(field='language')


def get_all_countries():
    return Source.objects.distinct(field='country')


def get_article_by_id(article_id):
    """
    Return article object
    Summarize here first
    :param article_id:
    :return: 
    """
    try:
        article = Article.objects.get(id=article_id)

        if not article.is_summarized:
            sum_article = update_summarized_article(article)
            if sum_article is not None:
                sum_article = update_sentiment_article(sum_article)
            if sum_article is not None:
                article = sum_article
                log.info(("Article:{0} summarized").format(article))
            else:
                log.info(("Article:{0}: failed to be summarized").format(article))

        elif needs_to_be_resummarized(article):
            sum_article = update_summarized_article(article, len(article.summary_sentences)+1)
            if sum_article is not None:
                article = sum_article
                log.info(("Article:{0} re-summarized").format(article))
            else:
                log.info(("Article:{0}: failed to be re-summarized").format(article))

        # Increment views in latest rating object
        article.ratings[-1].nb_views += 1
        article.save(cascade=True)
        article.ratings[-1].save()
        return_json = {}
        # Find 4 similar articles recently published
        similar_articles_list = similar_articles(article)
        if len(similar_articles_list):
            return_similar_json_list = [s_article.as_small_json() for s_article in similar_articles_list]
            # log.info(return_json_list)
            similarjson = json.dumps(return_similar_json_list)

            return_json = json.loads(article.to_json())

            return_json['similar_articles'] = similarjson

        return json.dumps(return_json)

    except Article.DoesNotExist:
        return json.dumps("{'status':'Does not exist Error'}")



def get_articles_from_category(category="General",
                               time_delta_ago=timedelta(days=TIME_THRESHOLD_CONSTANT_DAYS,
                                                        hours=TIME_THRESHOLD_CONSTANT_HOURS),
                               languages=DEFAULT_LANGUAGES_LIST,
                               countries=get_all_countries(),
                               pageNumber=1):
    """
    
    :param category: Possible options: business, entertainment, gaming, general, 
            music, politics, science-and-nature, sport, technology.
    :param time_delta_ago: Time to go back
    :param languages: Array of languages to filter for
    :param countries: Array of source countries to filter for
    :return: list of all articles to json
    """
    log.info("Fetching articles for category{0}, from {1} ago".format(category, time_delta_ago))
    time_threshold = datetime.utcnow() - time_delta_ago

    # Get all Articles with source in english
    # source_list = Source.objects.filter(Q(description__contains=category) | Q(category=category))

    source_list = Source.objects.filter(language='en').filter(country__in=countries)

    if len(source_list) > 0:
        article_list = Article.objects.filter(source__in=source_list)\
            .filter(published_at__gt=time_threshold)\
            .order_by('-published_at')

        # Some exceptions for categories
        if category.lower() == "General".lower():
            categories = ["General", "general", "Recreation"]
        elif category == "All":
            jsonCat = json.loads(get_all_categories())
            categories = jsonCat['categories']
        else:
            categories = [category]

        duplicate_article_list = []
        for cat in categories:
            duplicate_article_list += (article_list.filter(Q(category__icontains=cat)))

        setArticles = set(duplicate_article_list)
        article_list = list(setArticles)

        # Truncate based on page #
        try:
            pageNumber = int(pageNumber)
        except ValueError:
            pageNumber = 1

        hasNextPage = True
        if len(article_list) - NB_ARTICLES_PER_PAGE*pageNumber <= 0:
            hasNextPage = False


        article_list = article_list[(pageNumber-1)*NB_ARTICLES_PER_PAGE:pageNumber*NB_ARTICLES_PER_PAGE]

        # re-sort on published date
        article_list.sort(key=lambda x: x.published_at, reverse=True)

        log.info("Returns:{0} Articles for categories:{1}".format(len(article_list), categories))
        if len(article_list):
            return_json_list = [article.as_small_json() for article in article_list]
            # log.info(return_json_list)

            return_json = {"articles": return_json_list,
                           "hasNextPage": hasNextPage}

            return json.dumps(return_json)


            # return json.dumps(return_json_list)


def update_sentiment_article(article):
    return get_sentiment(article)


def update_summarized_article(article, nb_sentances=5):
    return summarize(article, nb_sentances)


def save_article_unsummarized(title, author, url, source, description, url_to_image,
                              published_at, nb_original_chars, category):
    """
    Checks if an article already exists from NewsApi, if not saves in DB
    :param title:
    :param author:
    :param url:
    :param source:
    :param description:
    :param url_to_image:
    :param published_at:
    :return:
    """
    try:
        article = Article.objects.get(url=url)
    except Article.DoesNotExist:
        article = None

    if article is None:
        article = Article(title=title, author=author, url=url, source=source, description=description,
                          url_to_image=url_to_image, published_at=published_at,
                          nb_original_chars=nb_original_chars, category=category)

        try:
            article.save()
            log.info(("Article:{0} saved into db").format(article))
        except ValidationError:
            log.info(("Article:{0} URL: {1} failed to be saved into db").format(title, url))

    #else:
       #log.info(("Article:{0} already exists in db").format(article))


def save_source(id, category, name, description, language, country, sortBysAvailable, urlsToLogos):
    """
    Save a source, if that source does not already exist
    :param id: 
    :param category: 
    :param name: 
    :param description: 
    :param language: 
    :param country: 
    :param sortBysAvailable: 
    :param urlsToLogos: 
    :return: 
    """

    try:
        source = Source.objects.get(source_id=id)
    except Source.DoesNotExist:
        source = None

    if source is None:
        source = Source(source_id=id, source_name=name, category=category, description=description, language=language,
                        country=country, sortBysAvailable=sortBysAvailable, urlsToLogos=urlsToLogos)

        try:
            source.save()
            log.info("New Source:{0} saved into db".format(source))
        except ValidationError:
            log.info("New Source:{0} failed to be saved into db".format(id))


def addRating(isUp, ratingID, nbSentences):
    """
    Increments the number of thumbs up or down for an article for a given number of sentences
    :param isUp:
    :param ratingID:
    :param nbSentences:
    :return:
    """
    try:
        rating = Rating.objects.get(id=ratingID)
        log.info("Found rating: {0}".format(ratingID))
        # article = Article.objects.get(id=article_id)
        # rating = None
        #
        # for ratingCandidate in article.ratings:
        #     if ratingCandidate.nb_sentences == nbSentences:
        #         rating = ratingCandidate
        #         break

        if rating is not None:
            if isUp:
                rating.nb_thumbs_up += 1
                log.info("Number of thumbs up incremented for article " + ratingID + " for " + nbSentences)
            else:
                rating.nb_thumbs_down += 1
                log.info("Number of thumbs down incremented for article " + ratingID + " for " + nbSentences)

            rating.save(cascade=True)
            # article.save()
        # else:
        #     # Must have been summarized without a rating object
        #     if isUp:
        #         rating = Rating(nb_thumbs_up=1, nb_thumbs_down=0, nb_sentences=nbSentences, nb_views=0)
        #         log.info("Number of thumbs up incremented for article " + article_id + " for " + nbSentences)
        #     else:
        #         rating = Rating(nb_thumbs_up=0, nb_thumbs_down=1, nb_sentences=nbSentences, nb_views=0)
        #         log.info("Number of thumbs down incremented for article " + article_id + " for " + nbSentences)
        #
        #     rating.save()
        #     article.ratings.append(rating)
        #     article.save()

        return json.dumps("{'status':'Done!'}")

    except Rating.DoesNotExist:
        return json.dumps("{'status':'Does not exist Error'}")


def needs_to_be_resummarized(article):
    """
    Checks ratings/views to see if there needs to be resummarize
    :param article:
    :return:
    """

    # get latest rating
    rating = article.ratings[-1]

    rating_thumbs_up = rating.nb_thumbs_up

    if rating.nb_thumbs_up == 0:
        rating_thumbs_up = 1

    if rating.nb_thumbs_down/rating_thumbs_up > UPDATE_SUMMARY_RATIO_THRESHOLD:
        return True
    else:
        return False


def similar_articles(article):
    """
    Returns similar articles to the one viewed published within +-12 Hours
    First similarity to already summarized articles, then to non via description
    :param article: 
    :return: 
    """
    keyWordList = article.keywords
    keyWordSet = set(keyWordList)

    minTime = article.published_at-timedelta(hours=12)
    maxTime = article.published_at+timedelta(hours=12)

    initial_candidateList = Article.objects.\
        filter(published_at__gt=minTime).\
        filter(published_at__lt=maxTime)

    candidateList = initial_candidateList.filter(keywords__in=keyWordList)

    # Assign score by article in terms of number of keywords that intersect
    similarityScoreTupleList = []

    for candidate in candidateList:
        intersectSet = keyWordSet.intersection(candidate.keywords)
        similarityScoreTupleList.append((candidate, len(intersectSet)))

    # Sort based on score
    similarityScoreTupleList.sort(key=lambda x: x[1], reverse=True)

    returnList = []
    similar_list_max = 4
    for articleTuple in similarityScoreTupleList:
        if articleTuple[0].id == article.id:
            continue
        returnList.append(articleTuple[0])

        if len(returnList) == similar_list_max:
            break

    # if keywords wasn't enough fill rest with similar ones based on article keywords all found in description
    if len(returnList) < 4:
        newCandidateList = Article.objects.\
            filter(published_at__gt=minTime).\
            filter(published_at__lt=maxTime)

        for keyword in article.keywords:
            # # initialize on first pass
            # if len(initial_candidateList) == 0:
            #     newCandidateList = initial_candidateList

            templist = newCandidateList
            newCandidateList = newCandidateList.filter(description__icontains=keyword)

            #One filter too much, break out with old values
            if len(newCandidateList) == 0:
                newCandidateList = templist
                break

        if len(newCandidateList) > 0:
            newCandidateList.order_by('-published_date')

            for newArticle in newCandidateList:
                if newArticle.id == article.id:
                    continue
                returnList.append(newArticle)

            # Truncate to 4
            del returnList[4:]

    return returnList


def find_articles_by_keywords_and_time(searchCriteriaString, maxTimeDelta=timedelta(days=7), pageNumber =1):
    """
    Return articles that match a search criteria and time
    :param searchCriteria: string of search criteria 
    :param maxTimeDelta: max relative time to look back until present
    :return: list of articles
    """

    searchCriteria = searchCriteriaString.split(' ')

    replacePlusList = []
    for criteria in searchCriteria:
        replacePlusList.append(criteria.replace('+', ' '))

    searchCriteria = replacePlusList

    time_threshold = datetime.utcnow() - maxTimeDelta

    candidateList = Article.objects.filter(published_at__gt=time_threshold)

    for criteria in searchCriteria:
        candidateList = candidateList.filter(Q(description__icontains=criteria) | Q(title__icontains=criteria))

    log.info("Returns:{0} Articles for search string:{1}".format(len(candidateList), searchCriteriaString))

    hasNextPage = True
    if len(candidateList) - NB_ARTICLES_PER_PAGE * pageNumber <= 0:
        hasNextPage = False

    candidateList = candidateList[(pageNumber - 1) * NB_ARTICLES_PER_PAGE:pageNumber * NB_ARTICLES_PER_PAGE]



    if len(candidateList):
        return_json_list = [article.as_small_json() for article in candidateList]
        # log.info(return_json_list)

        return_json = {"articles": return_json_list,
                       "hasNextPage": hasNextPage}

        return json.dumps(return_json)
    else:
        return json.dumps("{'status':'No articles match the search string'}")







