from django.shortcuts import render
from github.models import *
from django.template import RequestContext, loader
from django.http import HttpResponse
import requests, json, datetime, pickle, sys
from django.db.models.base import ObjectDoesNotExist
from django.db.models import Count, Min
from markdown import markdown

import logging
from django.views import generic
from processing import BulkImport, RateLimitRemaining, ProcessRepo

from django.conf import settings
from urllib import unquote

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

def Compare(request):
    template = loader.get_template('github/compare.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))

def Jasmine(request):
    template = loader.get_template('github/jasmine.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))

def About(request):
    template = loader.get_template('github/about.html')
    with open ('readme.md', 'r') as myFile:
        content = myFile.read()
    content = markdown(content)
    context = RequestContext(request, { 'content': content })
    return HttpResponse(template.render(context))

def QueueMonitorData(request):
    queueMonitorData = GitHubRequestCache.objects.values('success').annotate(Count('query'))
    
    myJson = {'unproccessed':0, 'successful':0, 'failed': 0}
    
    for queueData in queueMonitorData:
        if queueData['success'] == None:
            myJson['unproccessed'] = queueData['query__count']
        elif queueData['success'] == True:
            myJson['successful'] = queueData['query__count']
        elif queueData['success'] == False:
            myJson['failed'] = queueData['query__count']
            
    return HttpResponse(json.dumps(myJson))
    
def CompareData(request):
    #Initialize our JSON Object
    myJson = {'cols': [{'label':'Month','type':'string'}], 'rows':[]}

    #parse and sanitize our data
    full_names = unquote(request.GET.get('full_names'))

    if full_names =='':
        return HttpResponse(json.dumps(myJson))

    full_names = [n for n in full_names.split('+')]

    ### Populate Columns

    # Get Column Headers for Repos
    repos = Repo.objects.filter(full_name__in=full_names).values('id','full_name').order_by('id') # may want more data for the grid later

    #populate missing data
    full_names_queried = [n['full_name'] for n in repos]
    full_names_missing = list(set(full_names) - set(full_names_queried))

    for full_name in full_names_missing:
        #repos should auto-update after the insert/update mentho
        ProcessRepo(full_name)

    repos.update()

    #generate list of repo_ids for more efficient queries
    repo_ids = [n['id'] for n in repos]
    # need to be ordered from low to high
    repo_ids.sort()

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

    log.info(repoSummary.query)

    numberOfRepos = len(repo_ids)
    nextRepoToWrite = 0
    #initialize the first row
    myRow = {'c':[{'v':str(currentDate.year) + '-' + str(currentDate.month)}]}

    log.info(numberOfRepos)

    for repo in repoSummary:
        # check if the current repo is the right month

        if currentDate.month != repo['created_month'] or currentDate.year != repo['created_year']:
            # add blank rows until we've reached the repo's time frame
            while currentDate.month != repo['created_month'] or currentDate.year != repo['created_year']:
                # write our current row, we have a new time row to deal with.

                # pad out the columns with 0s otherwise the graph looks funky
                while nextRepoToWrite < numberOfRepos:
                    myRow['c'].append({'v':0})
                    nextRepoToWrite+=1

                # reset the column filter
                nextRepoToWrite = 0

                # note: this should write the current row first, and then leave us with a new empty row by the time the loop is finished.
                myJson['rows'].append(myRow)

                # set up a row of data
                currentDate = currentDate.replace(month=(currentDate.month) % 12 + 1, year=currentDate.year + currentDate.month / 12)
                month = str(currentDate.month)
                if (currentDate.month < 10):
                    month = "0" + month
                myRow = {'c':[{'v':str(currentDate.year) + '-' + month}]}


        # check if it's time to write the repos, or if we skipped one

        #no data for this column, pad with 0s
        while repo_ids[nextRepoToWrite] != repo['repo_id']:
            myRow['c'].append({'v':0})
            nextRepoToWrite+=1

        #write our column
        myRow['c'].append({'v':repo['created_count']})

        #increment column counter
        nextRepoToWrite = nextRepoToWrite + 1

    # append the last row of data
    myJson['rows'].append(myRow)

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
