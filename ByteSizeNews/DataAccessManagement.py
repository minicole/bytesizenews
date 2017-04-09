from ByteSizeNews.models import *
from ByteSizeNews.SummarizeService import *
from datetime import datetime, timedelta
from mongoengine.queryset.visitor import Q
import logging
import json

log = logging.getLogger(__name__)

TIME_THRESHOLD_CONSTANT_DAYS = 0
TIME_THRESHOLD_CONSTANT_HOURS = 5

def get_articles():
    return get_articles_from_category("")


def get_all_categories():
    return ["business", "entertainment", "gaming", "general",
            "music", "politics", "science-and-nature", "sport", "technology"]

def get_article_by_id(article_id):
    """
    Return article object
    Summarize here first
    :param url: 
    :return: 
    """
    try:
        article = Article.objects.get(id=article_id)

        if not article.is_summarized:
            sum_article = update_summarized_article(article)
            if sum_article is not None:
                article = sum_article
                log.info(("Article:{0} sumamrized").format(article))
            else:
                log.info(("Article:{0}: failed to be summarized").format(article))


        return article.to_json()

    except Article.DoesNotExist:
        return json.dumps("{'status':'Does not exist Error'}")


def get_articles_from_category(category, time_delta_ago=timedelta(days= TIME_THRESHOLD_CONSTANT_DAYS,hours=TIME_THRESHOLD_CONSTANT_HOURS)):
    """
    
    :param category: Possible options: business, entertainment, gaming, general, 
            music, politics, science-and-nature, sport, technology.
    :param time_delta_ago: Time to go back
    :return: list of all articles to json
    """

    time_threshold = datetime.now() - time_delta_ago

    # Get all sources with that category
    source_list = Source.objects.filter(Q(description__contains=category) | Q(category=category))

    if len(source_list) > 0:
        article_list = Article.objects.filter(source__in=source_list)\
            .filter(published_at__gt=time_threshold)\
            .order_by('published_at')

        if len(article_list):
            return_json_list = [article.as_small_json() for article in article_list]
            return json.dumps(return_json_list)



def update_summarized_article(article):
    return summarize(article)




def save_article_unsummarized(title, author, url, source, description, url_to_image, published_at):
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
                          url_to_image=url_to_image, published_at=published_at)

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


def addRating(isUp, article_id, nbSentences):
    """
    Increments the number of thumbs up or down for an article for a given number of sentences
    :param isUp:
    :param article_id:
    :param nbSentences:
    :return:
    """
    try:
        article = Article.objects.get(id=article_id)
        rating = article.ratings.objects.get(nb_sentences=nbSentences)

        if rating:
            if isUp:
                rating.nb_thumbs_up += 1
                log.info("Number of thumbs up incremented for article " + article_id + " for " + nbSentences)
            else:
                rating.nb_thumbs_down += 1
                log.info("Number of thumbs down incremented for article " + article_id + " for " + nbSentences)

            rating.save()
        else:
            if isUp:
                rating = Rating(nb_thumbs_up=1, nb_thumbs_down=0, nb_sentences=nbSentences)
                log.info("Number of thumbs up incremented for article " + article_id + " for " + nbSentences)
            else:
                rating = Rating(nb_thumbs_up=0, nb_thumbs_down=1, nb_sentences=nbSentences)
                log.info("Number of thumbs down incremented for article " + article_id + " for " + nbSentences)

            rating.save()
            article.ratings.append(rating)
            article.save()

        return json.dumps("{'status':'Done!'}")

    except Article.DoesNotExist:
        return json.dumps("{'status':'Does not exist Error'}")