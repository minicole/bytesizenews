from django.shortcuts import render
from django.http import HttpResponse, HttpRequest

import requests
from django.views.decorators.csrf import csrf_exempt

from ByteSizeNews.models import Article
from ByteSizeNews import DataAccessManagement
from django.core import serializers

import json

import logging

log = logging.getLogger('django')


@csrf_exempt
def get_all_articles(request, page):
    """
    Gets all the articles for all categories
    """
    articles = DataAccessManagement.get_articles(page)

    resp = HttpResponse(articles)
    resp.setdefault("Access-Control-Allow-Origin", "*")
    resp.setdefault('Access-Control-Allow-Methods', 'GET, POST')
    resp.setdefault("Access-Control-Allow-Headers", "Origin, Content-Type, X-Auth-Token")

    return resp


@csrf_exempt
def get_articles_from_category(request, category, page):
    articles = DataAccessManagement.get_articles_from_category(category, pageNumber=page)
    resp = HttpResponse(articles)
    resp.setdefault("Access-Control-Allow-Origin", "*")
    resp.setdefault('Access-Control-Allow-Methods', 'GET, POST')
    resp.setdefault("Access-Control-Allow-Headers", "Origin, Content-Type, X-Auth-Token")

    return resp


@csrf_exempt
def get_articles_from_search(request, page, hours, days, query):
    articles = DataAccessManagement.find_articles_by_keywords_and_time(query, hours, days, page)
    resp = HttpResponse(articles)
    resp.setdefault("Access-Control-Allow-Origin", "*")
    resp.setdefault('Access-Control-Allow-Methods', 'GET, POST')
    resp.setdefault("Access-Control-Allow-Headers", "Origin, Content-Type, X-Auth-Token")

    return resp


@csrf_exempt
def get_article(request, articleID):
    article = DataAccessManagement.get_article_by_id(articleID)
    resp = HttpResponse(article)
    resp.setdefault("Access-Control-Allow-Origin", "*")
    resp.setdefault('Access-Control-Allow-Methods', 'GET, POST')
    resp.setdefault("Access-Control-Allow-Headers", "Origin, Content-Type, X-Auth-Token")

    log.debug(resp)

    return resp


@csrf_exempt
def thumbsUp(request, ratingID, nbSentences):
    confirmation = DataAccessManagement.addRating(True, ratingID, nbSentences)

    resp = HttpResponse(confirmation)
    resp.setdefault("Access-Control-Allow-Origin", "*")
    resp.setdefault('Access-Control-Allow-Methods', 'GET, POST')
    resp.setdefault("Access-Control-Allow-Headers", "Origin, Content-Type, X-Auth-Token")

    return resp


@csrf_exempt
def thumbsDown(request, ratingID, nbSentences):
    confirmation = DataAccessManagement.addRating(False, ratingID, nbSentences)

    resp = HttpResponse(confirmation)
    resp.setdefault("Access-Control-Allow-Origin", "*")
    resp.setdefault('Access-Control-Allow-Methods', 'GET, POST')
    resp.setdefault("Access-Control-Allow-Headers", "Origin, Content-Type, X-Auth-Token")

    return resp