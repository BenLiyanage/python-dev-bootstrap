from django.shortcuts import render
from github.models import *
from django.template import RequestContext, loader
from django.http import HttpResponse
import requests, json, datetime, pickle, sys
from django.db.models.base import ObjectDoesNotExist
import logging
from django.views import generic
from django.conf import settings


log = logging.getLogger(__name__)
apiBaseURL = 'https://api.github.com/'

def BulkImport():
    output = "Initializing Population\n"    
    
    RefreshRateLimitStats()
    remaining = RateLimitRemaining('core')
    since = 0
    
    #while remaining > 4999:
    output += "{0} API Calls Left\n".format(remaining)
    
    #get open source repositories
    repoURL = 'repositories?since=' + str(since)
    r = MakeGitHubRequest(repoURL)
    counter = 0
    
    markAsProcessed = True
    if r:   
        for remoteRepo in r:
            # try to look up this repo
            
            if remoteRepo:
                output += ProcessRepo(remoteRepo["full_name"])
            else:
                output += "Repo Object" + json.dumps(remoteRepo, indent=4, separators=(',', ': '))
                markAsProcessed = False
        
        if markAsProcessed:
            MarkGitHubRequestAsProcessed(repoURL)
        # update stats on repo
    #need to do authentication stuff before rate limiting as I need more requests then the unauthenticated ones
    remaining = RateLimitRemaining('core')
    return output

def ProcessRepo(name):
    try:
        log.info("Getting id: {0}".format(name))
        output = ""
        
        remoteRepoURL = "repos/{0}".format(name)
        remoteRepo = MakeGitHubRequest(remoteRepoURL)
        
        if remoteRepo:
            try:
                myRepo = Repo.objects.get(pk = remoteRepo["id"])
            except ObjectDoesNotExist:
                myRepo = Repo(id = remoteRepo["id"])
            finally:
                # update base description
                myRepo.full_name = remoteRepo["full_name"]
                myRepo.description = remoteRepo["description"]
                myRepo.html_url = remoteRepo["html_url"]
                myRepo.save()
                MarkGitHubRequestAsProcessed(remoteRepoURL)
                
                # get pull requests
                # get request is dependant on ratelimiting parameters that we may have captured
                remotePullRequestURL = "repos/" + myRepo.full_name + "/pulls?state=closed"
                remotePullRequests = MakeGitHubRequest(remotePullRequestURL)
                
                if remotePullRequests is not None:
                    log.info("Importing {0} Pull Requests".format(len(remotePullRequests)))
                    for remotePullRequest in remotePullRequests:
                        try:
                            log.info("Processing Pull Number {0}".format(remotePullRequest['number']))
                            
                            try:
                                myPullRequest = myRepo.pullrequest_set.get(pk=remotePullRequest['number'])
                            except ObjectDoesNotExist:
                                myPullRequest = PullRequest(number = remotePullRequest['number'], repo = myRepo)
                            
                            #figure out if we need to create the user
                            if remotePullRequest['user'] is not None:
                                try:
                                    myUser = User.objects.get(pk = remotePullRequest['user']['id'])
                                except:
                                    myUser = User(pk = remotePullRequest['user']['id'], login = remotePullRequest['user']['login'])
                                    myUser.save()
                                
                            myPullRequest.user = myUser
                            
                            myPullRequest.state = remotePullRequest['state']
                            myPullRequest.created_at = remotePullRequest['created_at']
                            myPullRequest.updated_at = remotePullRequest['updated_at']
                            myPullRequest.closed_at = remotePullRequest['closed_at']
                            myPullRequest.merged_at = remotePullRequest['merged_at']

                            myPullRequest.save()
                        except Exception as e:
                            log.info("Failed to Process")
                            log.info(json.dumps(remotePullRequest, indent=4, separators=(',', ': ')))
                            raise
                        
                    output += str(list(myRepo.pullrequest_set.all()))
                    
                    MarkGitHubRequestAsProcessed(remotePullRequestURL)
            return output
        else:
            return "Could not process repo: {0}".format(name)
    except Exception as e:
        log.info("Error Proccessing Repo {0}".format(name))
        log.info(e)
        log.debug("Repo Object" + json.dumps(remoteRepo, indent=4, separators=(',', ': ')))
    
def RefreshRateLimitStats():
    rateInfo = MakeGitHubRequest('rate_limit')
    
    for myType in rateInfo['resources'].keys():
        type =str(myType)
        UpdateRateLimit(type, rateInfo['resources'][type]['limit'], rateInfo['resources'][type]['remaining'], rateInfo['resources'][type]['reset'])

def RateLimitRemaining(type):
    try:
        myRateLimit = RateLimit.objects.get(pk = type)
    except ObjectDoesNotExist:
        raise Exception("Missing Rate Limit Data, have things been initialized correctly?")
    
    return myRateLimit.remaining
        
    
def UpdateRateLimit(type, limit, remaining, reset):
    try:
        myRateLimit = RateLimit.objects.get(pk = type)
    except ObjectDoesNotExist:
        myRateLimit = RateLimit(type = type)
    
    myRateLimit.limit = limit
    myRateLimit.remaining = remaining
    s = int(limit)
    myRateLimit.reset = datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S.%f')
    myRateLimit.save()

def MarkGitHubRequestAsProcessed(url):
    #TODO: Process logic and logging is not completely right
    myRequestCache = GitHubRequestCache.objects.get(pk = url)
    myRequestCache.processed = True
    myRequestCache.save()
    
def MakeGitHubRequest(url):
    log.info("Making GitHubRequest: {0}".format(url))
    #look up our query to see if we can make a conditional request
    try:
        log.debug("Checking cache")
        myRequestCache = GitHubRequestCache.objects.get(pk = url)
        log.debug("Using ETag: {0}".format(myRequestCache.ETag))
    except ObjectDoesNotExist:
        log.debug("Unknown API Request")
        myRequestCache = GitHubRequestCache(pk = url, ETag = '')
    
    # Make the Request
    headers = {}
    if myRequestCache.processed:
        headers = {'If-None-Match':myRequestCache.ETag}
    
    #add auth stuff to our URL
    myURL = url
    if '?' in myURL:
        myURL += "&"
    else:
        myURL += "?"
    
    myURL += "client_id={0}&client_secret={1}".format(settings.GITHUB_CLIENTID, settings.GITHUB_CLIENTSECRET)
    r = requests.get(apiBaseURL + myURL, headers=headers)
    
    #record the new ETag
    if 'ETag' in r.headers:
        log.debug("Saving ETag: {0}".format(r.headers['ETag']))
        myRequestCache.ETag = r.headers['ETag']
        myRequestCache.save()
        
    #record rate limiting for status page
    type="core"
    if url.startswith("search"):
        type="search"
    
    UpdateRateLimit(type, r.headers['X-RateLimit-Limit'], r.headers['X-RateLimit-Remaining'], r.headers['X-RateLimit-Reset'])
    
    # check return status code
    if r.status_code == 200:
        log.debug("found new data")
        return r.json()
    elif r.status_code == 403:
        log.info(pickle.dumps(r.headers))
        log.info(json.dumps(r.json(), indent=4, separators=(',', ': ')))
        return None
    elif r.status_code == 304:
        #resource has not been modified, no processing needed
        log.debug("No new data found")
        return None
    else:
        raise Exception("Unknown StatusCode: {0}, {1}".format(r.status_code, url))