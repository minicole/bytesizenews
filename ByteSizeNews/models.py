from mongoengine import *


class Rating(Document):
    nb_sentences = IntField()
    nb_thumbs_up = IntField()
    nb_thumbs_down = IntField()


class Source(Document):
    category = StringField()
    source_id = StringField(unique=True, required=True)
    name = StringField()
    description = StringField()
    language = StringField()
    country = StringField()
    sortBysAvailable = ListField(StringField())
    urlsToLogos = ListField(StringField())

    def __str__ (self):
        return "{0}".format(self.source_id)


class Article(Document):
    title = StringField()
    author = StringField()
    url = URLField(unique=True, required=True)
    source = ReferenceField(Source)
    description = StringField()
    url_to_image = URLField()
    published_at = DateTimeField()
    is_summarized = BooleanField(default=False)
    summary_sentences = ListField(StringField())
    ratings = ListField(ReferenceField(Rating))
    keywords = ListField(StringField())
    sentiment = FloatField()

    def __str__ (self):
        return "{0}:{1}".format(self.title, self.url)
