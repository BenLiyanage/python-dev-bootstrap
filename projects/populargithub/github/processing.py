from django.shortcuts import render
from github.models import *
from django.template import RequestContext, loader
from django.http import HttpResponse
import requests, json, pickle, sys
from django.db.models.base import ObjectDoesNotExist
import logging
from django.views import generic
from django.conf import settings
from datetime import datetime, timedelta
from urllib import urlencode
from urlparse import urlparse, urlunparse, parse_qs


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
                remotePullRequestURL = "repos/" + myRepo.full_name + "/pulls?state=closed&per_page=100"

                ProcessPulLRequests(remotePullRequestURL, myRepo)

        else:
            log.info("Skipping, Repo Already Processed: {0}".format(name))
    except Exception as e:
        log.info("Error Proccessing Repo {0}".format(name))
        log.info(e)
        log.debug("Repo Object" + json.dumps(remoteRepo, indent=4, separators=(',', ': ')))

def ProcessPulLRequests(remotePullRequestURL, myRepo):
    remotePullRequests = MakeGitHubRequest(remotePullRequestURL)

    if remotePullRequests is not None:
        numberOfPullRequests = len(remotePullRequests)
        log.info("Importing {0} Pull Requests".format(numberOfPullRequests))
        if numberOfPullRequests > 0:
            log.info("Starting at Pull Request Number: {0}".format(remotePullRequests[0]['number']))

        for remotePullRequest in remotePullRequests:
            try:
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

        MarkGitHubRequestAsProcessed(remotePullRequestURL)


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
    myRateLimit.reset = datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S.%f')
    myRateLimit.save()

def MarkGitHubRequestAsProcessed(url):
    #TODO: Process logic and logging is not completely right
    myRequestCache = GitHubRequestCache.objects.get(query = url)
    myRequestCache.completed_at = datetime.now()
    if myRequestCache.success == None:
        myRequestCache.success = True
    myRequestCache.save()

def QueueGitHubRequest(url):
    try:
        myRequestCache = GitHubRequestCache.objects.get(query = url)
    except ObjectDoesNotExist:
        myRequestCache = GitHubRequestCache(query = url, ETag = '')

    myRequestCache.started_at = None
    myRequestCache.completed_at = None
    myRequestCache.save()

def ProcessGitHubRequest(numberToProcess=10):
    log.info("----------------------")
    log.info("Processing Queue")
    myRequestCaches = GitHubRequestCache.objects.filter(started_at__isnull = True).order_by('created_at')[:numberToProcess]

    for myRequestCache in myRequestCaches:
        queryParameters = myRequestCache.query.split('/')
        queryType = queryParameters [0]
        log.info("found a request")
        if queryType == 'repos':
            log.info("processing a repo")
            user = queryParameters[1]
            repo = queryParameters[2]

            ProcessRepo(user + '/' + repo)
        # pagination uses a different edge to process pull requests.  format is repositories/{id}/pulls?state=closed&page={pagenumber}
        elif queryType == 'repositories':
            #parse the repo from the url
            repoID = int(queryParameters[1])
            myRepo = Repo.objects.get(pk = repoID)

            delta = timedelta(days=settings.CACHE_DAYS_THRESHOLD)
            now = datetime.now()
            threshold = now - delta
            myPullRequest = PullRequest.objects.filter(repo_id=repoID, created_at__lte=threshold)

            if len(myPullRequest) > 0:
                myRequestCache.delete()
            else:
                #process the pull request
                ProcessPulLRequests(myRequestCache.query, myRepo)

        else:
            log.info("Unknown Request in Cache: {0}".format(myRequestCache.query))
            # mark this request as unproccessible
            myRequestCache.success = False
            myRequestCache.save()
            MarkGitHubRequestAsProcessed(myRequestCache.query)

    log.info("End Queue Processing")


def MakeGitHubRequest(url):
    log.info("Making GitHubRequest: {0}".format(url))
    #look up our query to see if we can make a conditional request
    try:
        log.info("Checking cache")
        myRequestCache = GitHubRequestCache.objects.get(query = url)
        log.info("Using ETag: {0}".format(myRequestCache.ETag))
    except ObjectDoesNotExist:
        log.info("API Request Not In Cache")
        myRequestCache = GitHubRequestCache(query = url, ETag = '')

    # Make the Request
    headers = {}
    if myRequestCache.completed_at != None:
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
        myRequestCache.started_at = datetime.now()
        myRequestCache.save()

    #record rate limiting for status page
    type="core"
    if url.startswith("search"):
        type="search"

    UpdateRateLimit(type, r.headers['X-RateLimit-Limit'], r.headers['X-RateLimit-Remaining'], r.headers['X-RateLimit-Reset'])

    # check for pagination.  If there is a paginated request, queue it.
    if 'Link' in r.headers:
        links = r.headers['Link'].split(',')

        for linkString in links:
            linkStringDecomposed = linkString.split('; ')
            if linkStringDecomposed[1] == 'rel="next"':

                nextLink = linkStringDecomposed[0][1:-1] # slice off the begining '<' and trailing '>'
                log.info("Raw Pagination Request {0}".format(nextLink))
                # remove client and secret from query
                u = urlparse(nextLink)
                query = parse_qs(u.query)
                query.pop('client_id', None)
                query.pop('client_secret', None)
                u = u._replace(query=urlencode(query, True))
                #queue the link
                nextLink = u.path + '?' + u.params + u.query
                nextLink = nextLink [1:] # remove leading '/'
                log.info("Queueing a pagination request: {0}".format(nextLink))
                QueueGitHubRequest(nextLink)

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