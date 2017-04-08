from mongoengine import *


class Rating(Document):
    nb_sentences = IntField()
    nb_thumbs_up = IntField()
    nb_thumbs_down = IntField()

class Article(Document):
    title = StringField()
    author = StringField()
    url = URLField(unique=True, required=True)
    type = StringField()
    source = StringField()
    description = StringField()
    url_to_image = URLField()
    published_at = DateTimeField()
    is_summarized = BooleanField(default=False)
    summary_sentences = ListField(StringField())
    ratings = ListField(ReferenceField(Rating))
    keywords = ListField(StringField())
    sentiment = FloatField()

    def __str__ (self):
        return ("{0} : {1}").format(self.title, self.url)
