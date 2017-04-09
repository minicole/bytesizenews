from ByteSizeNews.models import *
import logging

log = logging.getLogger(__name__)

def get_articles():
    return [Article(title="article1", author="author1",url="url1"),Article(title="article2", author="author2",url="url2")]


def get_articles_from_category(category):
    return [Article(title="article1cat1", author="author1",url="url1"),Article(title="article2cat1", author="author2",url="url2")]


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
        article.save()
        log.info(("Article:{0} saved into db").format(article))
    else:
        log.info(("Article:{0} already exists in db").format(article))


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
        source.save()
        log.info("New Source:{0} saved into db".format(source))
