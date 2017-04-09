from ByteSizeNews.models import *
from mongoengine.queryset.visitor import Q
import logging
import json

log = logging.getLogger(__name__)

def get_articles():
    return [Article(title="article1", author="author1", url="url1").to_json(),
            Article(title="article2", author="author2", url="url2").to_json()]

def get_all_categories():
    return ["business", "entertainment", "gaming", "general",
            "music", "politics", "science-and-nature", "sport", "technology"]

def get_article_by_url(url):
    """
    Return article object
    Summarize here first
    :param url: 
    :return: 
    """
    try:
        article = Article.objects.get(url=url)
        return article.to_json()

    except Article.DoesNotExist:
        return json.dumps("{'status':'Does not exist Error'}")

def get_articles_from_category(category):
    """
    
    :param category: Possible options: business, entertainment, gaming, general, 
            music, politics, science-and-nature, sport, technology.
    :return: list of all articles to json
    """

    # Get all sources with that category
    source_list = Source.objects.filter(Q(description__contains=category) | Q(category=category))
    if len(source_list) > 0:
        article_list = Article.objects.filter(source__in=source_list)

        if len(article_list):
            return_json_list = [article.as_small_json() for article in article_list]
            return json.dumps(return_json_list)

        # return [Article(title="article1cat1", author="author1", url="url1").to_json(),
        #     Article(title="article2cat1", author="author2", url="url2").to_json()]



def update_summarized_article(article):
    pass



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

