# Load url from database

from django.conf import settings
import requests

apirequestheader = "http://api.smmry.com/&SM_API_KEY="+settings.SMMRY_KEY+"&SM_KEYWORD_COUNT=5&SM_WITH_BREAK"


def summarize(article, numberOfSentances=7):
    # Build API request
    apirequest = apirequestheader+"&SM_LENGTH="+str(numberOfSentances)+"&SM_URL="+article.url
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





