from django.shortcuts import render
from django.http import HttpResponse, HttpRequest

import requests
from django.views.decorators.csrf import csrf_exempt

from ByteSizeNews.models import Article
from ByteSizeNews import DataAccessManagement
from django.core import serializers

import json


@csrf_exempt
def get_all_articles(request):
    """
    Gets all the articles for all categories
    """
    articles = DataAccessManagement.get_articles()
    articles_serialized = json.dumps(articles)

    resp = HttpResponse(articles_serialized)
    resp.setdefault("Access-Control-Allow-Origin", "*")
    resp.setdefault('Access-Control-Allow-Methods', 'GET, POST')
    resp.setdefault("Access-Control-Allow-Headers", "Origin, Content-Type, X-Auth-Token")

    return resp


@csrf_exempt
def get_articles_from_category(request, category):
    articles = DataAccessManagement.get_articles_from_category(category)
    articles_serialized = json.dumps(articles)

    resp = HttpResponse(articles_serialized)
    resp.setdefault("Access-Control-Allow-Origin", "*")
    resp.setdefault('Access-Control-Allow-Methods', 'GET, POST')
    resp.setdefault("Access-Control-Allow-Headers", "Origin, Content-Type, X-Auth-Token")

    return resp