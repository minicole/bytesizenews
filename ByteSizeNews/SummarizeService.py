# Load url from database

from django.conf import settings
from ByteSizeNews.models import Rating
import requests
import logging

log = logging.getLogger('django')

apirequestheader = "http://api.smmry.com/&SM_API_KEY={0}&SM_KEYWORD_COUNT=5&SM_WITH_BREAK&SM_QUOTE_AVOID"\
    .format(settings.SMMRY_KEY)


def summarize(article, numberOfSentances):
    # Build API request
    apirequest = "{0}&SM_LENGTH={1}&SM_URL={2}".format(apirequestheader, str(numberOfSentances), article.url)
    r = requests.get(apirequest)
    jsonresponse = r.json()

    if 'sm_api_error' not in jsonresponse:
        apiLimitation = jsonresponse['sm_api_limitation']


        keywordArray = jsonresponse['sm_api_keyword_array']
        newsTitle = jsonresponse['sm_api_title']
        charCount = jsonresponse['sm_api_character_count']
        summarizedContent = jsonresponse['sm_api_content'].split("[BREAK]")

        # Remove last blank in the split
        if summarizedContent[-1] == "":
            summarizedContent = summarizedContent[:-1]

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
            article.save(cascade=True)
            return article
        except:
            return None
        # print("Keywords:"+",".join(keywordArray))
        # print("Title:"+newsTitle)
        # print("Characters:"+charCount)
        # print("Content:"+"\n".join(summarizedContent))
        # print("Error:"+errorResponse)
    elif 'sm_api_message' in jsonresponse:
        log.info(jsonresponse['sm_api_message'])

        # attemt with unsummarized text
        if article.unsummarized_text is not None and article.unsummarized_text is not "":

            # create post request
            payload = {'sm_api_input': article.unsummarized_text}
            request = "{0}&SM_LENGTH={1}".format(apirequestheader,numberOfSentances)

            r = requests.get(request, data=payload)
            jsonresponse = r.json()

            if 'sm_api_error' not in jsonresponse:


                keywordArray = jsonresponse['sm_api_keyword_array']
                charCount = jsonresponse['sm_api_character_count']
                summarizedContent = jsonresponse['sm_api_content'].split("[BREAK]")

                # Remove last blank in the split
                if summarizedContent[-1] == "":
                    summarizedContent = summarizedContent[:-1]

                try:
                    article.summary_sentences = summarizedContent
                    article.keywords = keywordArray
                    article.is_summarized = True

                    # Create new rating object and set to 0/0/0 and save
                    rating = Rating(nb_sentences=numberOfSentances, nb_thumbs_down=0, nb_thumbs_up=0, nb_views=0,
                                    nb_summarized_chars=charCount)
                    rating.save()
                    article.ratings.append(rating)
                    article.save(cascade=True)
                    return article
                except:
                    return None



            elif 'sm_api_message' in jsonresponse:
                log.info(jsonresponse['sm_api_message'])
                return  None






# test

#summarize("http://www.abc.net.au/news/2017-04-05/victorian-police-and-afp-record-ice-haul-drugs-meth/8416718")





