from ByteSizeNews.models import Article
import logging

log = logging.getLogger(__name__)

def get_articles():
    return [Article(title="article1", author="author1",url="url1"),Article(title="article2", author="author2",url="url2")]


def get_articles_from_category(category):
    return [Article(title="article1cat1", author="author1",url="url1"),Article(title="article2cat1", author="author2",url="url2")]

def save_article_unsummarized(title, author, url, type, source, description,url_to_image,published_at):
    """
    Checks if an article already exists from NewsApi, if not saves in DB
    :param title:
    :param author:
    :param url:
    :param type:
    :param source:
    :param description:
    :param url_to_image:
    :param published_at:
    :return:
    """
    article = Article.objects.get(url=url)
    if not :
        article = Article(title=title,author=author,url=url,type=type,source=source,description=description,url_to_image=url_to_image, published_at=publisjed_at)
        article.save()
        log.info(("Article:{0} saved int db").format(article))
    else:
        log.info(("Article:{0} already exists in db").format(article))
