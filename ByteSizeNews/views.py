from django.shortcuts import render
from django.http import HttpResponse, HttpRequest

import requests

from ByteSizeNews.models import Article
from django.core import serializers
from ByteSizeNews import DataAccessManagment

import json


'''
Gets all the articles for all categories
'''
def get_all_articles(request):
    articles = DataAccessManagment.get_articles()
    articles_serialized = serializers.serialize('json', articles)

    return requests.post(request.get_host(), json=articles_serialized)


def get_articles_from_category(request, category):
    articles = DataAccessManagment.get_articles_from_category(category)
    articles_serialized = json.dumps(articles)

    return requests.post(request.get_host(), json=articles_serialized)