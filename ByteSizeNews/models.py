from mongoengine import *
from bson import json_util


class Rating(Document):
    nb_sentences = IntField()
    nb_thumbs_up = IntField()
    nb_thumbs_down = IntField()
    nb_views = IntField()
    nb_summarized_chars = IntField()


class Source(Document):
    category = StringField()
    source_id = StringField(unique=True, required=True)
    source_name = StringField()
    description = StringField()
    language = StringField()
    country = StringField()
    sortBysAvailable = ListField(StringField())
    urlsToLogos = ListField(StringField())

    def __str__(self):
        return "{0}".format(self.source_id)

    def as_small_json(self):
        return dict(
            source_id=self.source_id,
            category=self.category,
            source_name=self.source_name,
            language=self.language,
            country=self.country,
            urlsToLogos=self.urlsToLogos[2]  # Hard coded to medium? Or large For now
        )


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
    nb_original_chars = IntField()
    category = StringField()

    def __str__(self):
        return "{0}:{1}".format(self.title, self.url)

    def as_small_json(self):
        """
        Simplfied model of the full model
        :return: 
        """
        return dict(
            id=str(self.id),
            url=self.url,
            url_to_image=self.url_to_image,
            published_at=self.published_at.isoformat(),
            source=self.source.as_small_json(),
            author=self.author,
            title=self.title,
            description=self.description)

    def to_json(self):
        mongo_article = self.to_mongo() # pymongo representtion of the doc

        # Replace the source with the mongo representation of that
        mongo_article["source"] = Source.objects.get(id=str(mongo_article["source"])).to_mongo()

        #Replace ratings with their mongo representation as well
        temp_list = []
        for mongo_rating_obj in mongo_article["ratings"]:
            temp_list.append(Rating.objects.get(id=str(mongo_rating_obj)).to_mongo())

        #overwrite the articles
        mongo_article["ratings"] = temp_list
        return json_util.dumps(mongo_article)

