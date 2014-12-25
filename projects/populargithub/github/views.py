from django.shortcuts import render
from github.models import *
from django.template import RequestContext, loader
from django.http import HttpResponse
import requests, json, datetime, pickle, sys
from django.db.models.base import ObjectDoesNotExist
from django.db.models import Count, Min

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
    template = loader.get_template('github/graph.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))

def CompareData(request):
    #TODO: Replace with dynamic values
    repo_ids = [364,360,322]
    
    #Initialize our JSON Object
    myJson = {'cols': [{'label':'Month','type':'string'}], 'rows':[{'c':[{'v':'2004'},{'v':1000},{'v':400}]}]}
    
    ### Populate Columns
    
    # Get Column Headers for Repos
    repos = Repo.objects.filter(id__in=repo_ids).values('id','full_name').order_by('id') # may want more data for the grid later
    
    for repo in repos:
        myJson['cols'].append({'label':repo['full_name'],'type':'number'})
    
    #### Populate Rows
    today = datetime.date.today()
    firstDate = PullRequest.objects.filter(repo_id__in = repo_ids).aggregate(Min('created_at'))['created_at__min']
    currentDate = datetime.date(firstDate.year, firstDate.month, 1)
    
    #DATE filter part
    #.extra(where=['created_at > DATE_ADD(CURDATE(), INTERVAL -3 MONTH)']) \
    repoSummary = PullRequest.objects.filter(repo_id__in=repo_ids) \
        .extra(select={'created_year' : 'YEAR(created_at)'}) \
        .extra(select={'created_month' : 'MONTH(created_at)' }) \
        .values('repo_id','created_year', 'created_month') \
        .annotate(created_count=Count('repo_id')) \
        .order_by('created_year','created_month','repo_id')
    
    nextRepoToWrite=1
    numberOfRepos = len(repo_ids)
    nextRepoIndex = 0
    nextRepo = repoSummary[0]
    myRow = None
    
    # this while loop is bad and should be changed to a for loop over the query set
    while currentDate < today:
        if nextRepoIndex >= len(repoSummary):
            break
        
        if nextRepo is None:
            nextRepo = repoSummary[nextRepoIndex]
        #prime a row array
        if not myRow:
            myRow = {'c':[{'v':str(currentDate.year) + '-' + str(currentDate.month)}]}
        
        #check if the current repo is in the right year
        if currentDate.month == nextRepo['created_month'] and currentDate.year == nextRepo['created_year']:
            #check if its time to write the current repo's column
            if repo_ids[nextRepoToWrite] == nextRepo['repo_id']:
                #write the count
                myRow['c'].append({'v':nextRepo['created_count']})
                #reset the repo so we grab another
                nextRepoIndex = nextRepoIndex+1
                nextRepo = None
            else:
                #write 0
                myRow['c'].append({'v':0})
            
            #increment nextRepoToWrite
            nextRepoToWrite = nextRepoToWrite + 1 % numberOfRepos -1
        else:
            #append current row and start a new one
            
            currentDate = currentDate.replace(month=(currentDate.month+1) % 12, year=currentDate.year + (currentDate.month+1) % 13)
            myJson['rows'].append(myRow)
            myRow = None
            continue
   
    #myJson['rows'].append({'c':[{'v':'2008'},{'v':500},{'v':400},{'v':1000}]})
    return HttpResponse(json.dumps(myJson))

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
