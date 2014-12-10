from django.shortcuts import render
from github.models import *
from django.template import RequestContext, loader
from django.http import HttpResponse
import requests, json, datetime, pickle, sys
from django.db.models.base import ObjectDoesNotExist
import logging
from django.views import generic
from processing import BulkImport, RateLimitRemaining

from django.conf import settings

log = logging.getLogger(__name__)
apiBaseURL = 'https://api.github.com/'

class RepoList(generic.ListView):
    
    model = Repo

# Create your views here.
def QueueStatus(request):
    myRateLimit = RateLimit.objects.all()
    template = loader.get_template('github/ratelimit.html')
    context = RequestContext(request, { 'myRateLimit': myRateLimit})
    return HttpResponse(template.render(context))

def Graph(request):
    #timeRange = 
    repoSet = Repo.objects.all()[10:]
    template = loader.get_template('github/graph.html')
    context = RequestContext(request, {'repoSet': repoSet })
    return HttpResponse(template.render(context))

def GetStats(request):
    fullName = request.GET.get('full_name')
    ProcessRepo()
    myRepo = Repo.object.get(full_name = fullName)
    return 
    
def populate(request):
    output = BulkImport()
        
    #need to do authentication stuff before rate limiting as I need more requests then the unauthenticated ones
    remaining = RateLimitRemaining('core')
    return HttpResponse("<pre>" + output + "</pre>")
