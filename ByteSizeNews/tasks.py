from celery.decorators import task
from celery.utils.log import get_task_logger
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from ByteSizeNews.NewsFetchService import fetch_latest_news


logger = get_task_logger(__name__)

NewsFetchingPeriod = '*/1'

@periodic_task(run_every=(crontab(minute=NewsFetchingPeriod)), name="news_fetching_task", ignore_result=True)
def fetch_news(filter="latest"):
    """fetch article from newsapi service"""
    logger.info("Article fetcher")
    fetch_latest_news()