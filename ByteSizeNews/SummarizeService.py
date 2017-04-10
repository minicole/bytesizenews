# Load url from database

from django.conf import settings
from ByteSizeNews.models import Rating
import requests

apirequestheader = "http://api.smmry.com/&SM_API_KEY={0}&SM_KEYWORD_COUNT=5&SM_WITH_BREAK&SM_QUOTE_AVOID"\
    .format(settings.SMMRY_KEY)


def summarize(article, numberOfSentances):
    # Build API request
    apirequest = "{0}&SM_LENGTH={1}&SM_URL={2}".format(apirequestheader, str(numberOfSentances), article.url)
    r = requests.get(apirequest)
    jsonresponse = r.json()

    keywordArray = jsonresponse['sm_api_keyword_array']
    newsTitle = jsonresponse['sm_api_title']
    charCount = jsonresponse['sm_api_character_count']
    errorResponse = jsonresponse['sm_api_limitation']
    summarizedContent = jsonresponse['sm_api_content'].split("[BREAK]")

    # Check the error response here
    try:
        article.summary_sentences = summarizedContent
        article.keywords = keywordArray
        article.is_summarized = True

        # Create new rating object and set to 0/0/0 and save
        rating = Rating(nb_sentences=numberOfSentances, nb_thumbs_down=0, nb_thumbs_up=0, nb_views=0,
                        nb_summarized_chars=charCount)
        rating.save()
        article.ratings.append(rating)
        article.save()
        return article
    except:
        return None
    # print("Keywords:"+",".join(keywordArray))
    # print("Title:"+newsTitle)
    # print("Characters:"+charCount)
    # print("Content:"+"\n".join(summarizedContent))
    # print("Error:"+errorResponse)


# test

#summarize("http://www.abc.net.au/news/2017-04-05/victorian-police-and-afp-record-ice-haul-drugs-meth/8416718")





