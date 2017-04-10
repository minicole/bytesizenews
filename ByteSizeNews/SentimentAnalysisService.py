# Load url from database

from django.conf import settings
import http.client, urllib.request, urllib.parse, urllib.error, base64
from ByteSizeNews.SummarizeService import *
import json

headers = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': settings.MCS_TEXT_KEY,
}

params = urllib.parse.urlencode({
})


def get_sentiment(article):
    """
    Gets the sentiment analysis of the article and stores it in the db
    :param article:
    :return:
    """
    body = {
        "documents": [
            {
                "language": "en",
                "id": "idField",
                "text": ""
            }
        ]
    }

    if not article.is_summarized:
        article = summarize(article)

    for sentence in article.summary_sentences:
        body["documents"][0]["text"] += sentence

    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/text/analytics/v2.0/sentiment?%s" % params, str(body).encode(), headers)
        response = conn.getresponse()
        data = response.read().decode()
        dataObj = json.loads(data)
        article.sentiment = dataObj["documents"][0]["score"]
        article.save()
        conn.close()
        print(article)
        return article
    except Exception as e:
        print(e)


def get_sentiment_from_text(article):
    """
    Used to test
    :param article:
    :return:
    """
    body = str({
        "documents": [
            {
                "language": "en",
                "id": "string",
                "text": article
            }
        ]
    }).encode()

    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        print(params)
        print(body)
        print(headers)
        conn.request("POST", "/text/analytics/v2.0/sentiment?%s" % params, body, headers)
        print("sent")
        response = conn.getresponse()
        print(response)
        data = response.read()
        print(data)
        article.sentiment = data.documents.score
        article.save()
        conn.close()
        return article
    except Exception as e:
        print(e)
