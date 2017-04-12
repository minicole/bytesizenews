"""ByteSizeNews URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from ByteSizeNews import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^articles/(?P<page>[0-9]+)/(?P<category>[a-zA-Z]+)/', views.get_articles_from_category),
    url(r'^articles/(?P<page>[0-9]+)/',views.get_all_articles),
    url(r'^search/(?P<page>[0-9]+)/(?P<page>[0-9]+)/(?P<hours>[0-9]+)/(?P<days>[0-9]+)/(?P<query>.+)/', views.get_articles_from_search),
    url(r'^article/(?P<articleID>[0-9a-zA-Z]+)/', views.get_article),
    url(r'^thumbsup/(?P<ratingID>[0-9a-zA-Z]+)/(?P<nbSentences>[0-9]+)/', views.thumbsUp),
    url(r'^thumbsdown/(?P<ratingID>[0-9a-zA-Z]+)/(?P<nbSentences>[0-9]+)/', views.thumbsDown),
]
