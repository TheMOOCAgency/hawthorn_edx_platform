"""
TMA APPS endpoint urls.
"""

from django.conf.urls import url
from django.conf import settings
from certificates.views import ensure, render

urlpatterns = (
    #certificates
    url(r'^{}/certificate/ensure$'.format(settings.COURSE_ID_PATTERN), ensure, name="ensure"),
    url(r'^{}/certificate/render$'.format(settings.COURSE_ID_PATTERN), render, name="render"),
)
