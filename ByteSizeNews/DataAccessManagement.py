from ByteSizeNews.models import *
from ByteSizeNews.SummarizeService import *
from ByteSizeNews.SentimentAnalysisService import *
from datetime import datetime, timedelta
from mongoengine.queryset.visitor import Q
import logging
import json

log = logging.getLogger('django')

TIME_THRESHOLD_CONSTANT_DAYS = 0
TIME_THRESHOLD_CONSTANT_HOURS = 5

DEFAULT_LANGUAGES_LIST = ["en"]


def get_articles():
    return get_articles_from_category("All")


def get_all_categories():
    categorieslist = Article.objects.distinct(field='category')

    #Only general available
    if(categorieslist<2):
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
        return article.to_json()

    except Article.DoesNotExist:
        return json.dumps("{'status':'Does not exist Error'}")


# TODO: Replace category with a list
def get_articles_from_category(category="General",
                               time_delta_ago=timedelta(days=TIME_THRESHOLD_CONSTANT_DAYS,
                                                        hours=TIME_THRESHOLD_CONSTANT_HOURS),
                               languages=DEFAULT_LANGUAGES_LIST,
                               countries=get_all_countries()):
    """
    
    :param category: Possible options: business, entertainment, gaming, general, 
            music, politics, science-and-nature, sport, technology.
    :param time_delta_ago: Time to go back
    :param languages: Array of languages to filter for
    :param countries: Array of source countries to filter for
    :return: list of all articles to json
    """

    time_threshold = datetime.utcnow() - time_delta_ago

    # Get all Articles with source in english
    # source_list = Source.objects.filter(Q(description__contains=category) | Q(category=category))

    source_list = Source.objects.filter(language='en').filter(country__in=countries)

    if len(source_list) > 0:
        article_list = Article.objects.filter(source__in=source_list)\
            .filter(published_at__gt=time_threshold)\
            .order_by('published_at')

        # Some exceptions for categories

        if category == "General":
            categories = ["General", "general", "Recreation"]
        elif category == "All":
            categories = get_all_categories()['categories']
        else:
            categories = [category]

        duplicate_article_list = []
        for cat in categories:
            duplicate_article_list += (article_list.filter(Q(category=cat)))

        setArticles = set(duplicate_article_list)
        article_list = list(setArticles)
        log.info("Returns:{0} Articles".format(len(article_list)))
        if len(article_list):
            return_json_list = [article.as_small_json() for article in article_list]
            # log.info(return_json_list)
            return json.dumps(return_json_list)


def update_sentiment_article(article):
    return get_sentiment(article)


def update_summarized_article(article, nb_sentances=7):
    return summarize(article, nb_sentances)


def save_article_unsummarized(title, author, url, source, description, url_to_image, published_at, nb_original_chars, category):
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

    if rating.nb_thumbs_down/rating_thumbs_up > 3.0:
        return True
    else:
        return False
