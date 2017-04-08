from ByteSizeNews.models import Article


def get_articles():
    return [Article(title="article1", author="author1",url="url1"),Article(title="article2", author="author2",url="url2")]


def get_articles_from_category(category):
    return [Article(title="article1cat1", author="author1",url="url1"),Article(title="article2cat1", author="author2",url="url2")]