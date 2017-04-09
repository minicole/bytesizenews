from celery.decorators import task
from celery.utils.log import get_task_logger
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from ByteSizeNews.NewsFetchService import *


logger = get_task_logger(__name__)

# Fetch on the hour  0 minutes crontab notation
if DEBUG:
    NewsFetchingPeriod = '*/5'
    SourceFetchingPeriod = '*/3'
else:
    NewsFetchingPeriod = '*/45'

@periodic_task(run_every=(crontab(minute=0)), name="news_fetching_task", ignore_result=True)
def fetch_news(filter="latest"):
    """fetch article from newsapi service"""
    fetch_and_save_latest_news()


# Fetch and update sources at midnight every day
# @periodic_task(run_every=(crontab(minute=SourceFetchingPeriod)), name="sources_fetching_task", ignore_result=True)
@periodic_task(run_every=(crontab(minute=10, hour=0)), name="sources_fetching_task", ignore_result=True)
def fetch_sources():
    """fetch article from newsapi service"""
    fetch_save_and_update_sources()
