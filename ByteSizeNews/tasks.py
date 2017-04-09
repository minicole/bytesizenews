from celery.decorators import task
from celery.utils.log import get_task_logger
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from ByteSizeNews.NewsFetchService import fetch_latest_news


logger = get_task_logger(__name__)

# Fetch every 45 minutes crontab notation
NewsFetchingPeriod = '*/45'

@periodic_task(run_every=(crontab(minute=NewsFetchingPeriod)), name="news_fetching_task", ignore_result=True)
def fetch_news(filter="latest"):
    """fetch article from newsapi service"""
    fetch_latest_news()