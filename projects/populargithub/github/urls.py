from django.conf.urls import patterns, url, include
from github import views
from django.views.generic import DetailView, ListView

urlpatterns = patterns('',
    url(r'^queuestatus$', views.QueueStatus, name='QueueStatus'),
    url(r'^compare$', views.Compare, name='compare'),
    url(r'^populate$', views.populate, name='populate'),
    url(r'^repo$', views.RepoList.as_view(), name='populate'),
    url(r'^comparedata$', views.CompareData),
    url(r'^jasmine$', views.Jasmine, name='jasmine'),
)