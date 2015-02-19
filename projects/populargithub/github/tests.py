from django.test import TestCase
from models import Repo, PullRequest, User
from processing import ProcessRepo, GitHubRequestCache, QueueGitHubRequest, ProcessGitHubRequest
from django.db.models.base import ObjectDoesNotExist
import unittest
from random import choice
# Create your tests here.

class TestProccessing(TestCase):
    def test_ProcessRepo(self):
        testRepo = 18295962
        testRepoFullName = 'BenLiyanage/vagrant-python'

        # Proccess a known repo
        ProcessRepo(testRepoFullName)

        # test some default values
        myRepo = Repo.objects.get(pk = testRepo)
        self.assertEqual(myRepo.full_name, testRepoFullName)
        # test that pull requests got imported
        self.assertGreater(myRepo.pullrequest_set.count(), 0)

        # test that the github request was processed
        myRequestCache = GitHubRequestCache.objects.get(query = 'repos/' + testRepoFullName)
        self.assertNotEqual(myRequestCache.started_at, None)
        self.assertNotEqual(myRequestCache.completed_at, None)

        #repo request shouldn't be processed, since its cached
        ProcessRepo(testRepoFullName)

    def test_PrcoessRepoLargePullRequestCount(self):
        testRepo = 3638964
        testRepoFullName = 'ansible/ansible'

        # Proccess a known repo
        ProcessRepo(testRepoFullName)

        # verify that a pagination was queued on the pullrequest import
        myRequestCaches = GitHubRequestCache.objects.filter(started_at__isnull = True)
        self.assertEqual(myRequestCaches.count(), 1)

        # process the queued pagination
        ProcessGitHubRequest(1)

        myRepo = Repo.objects.get(pk = testRepo)

        # test that pull requests got imported
        # this repo should have more than 100 pull requests.
        # importing pull requests requires pagingation to go over 100 entries
        self.assertGreater(myRepo.pullrequest_set.count(), 100)

        #verify that another request was queued
        myRequestCaches = GitHubRequestCache.objects.filter(started_at__isnull = True)
        self.assertEqual(myRequestCaches.count(), 1)

        #### Test hitting the data cache threshold for large pull request chains.
        # get a random user_id
        myUser = choice(User.objects.all())

        myPullRequest = PullRequest(number = 10000,repo=myRepo, created_at = '2013-01-01 01:01', user = myUser, updated_at='2015-01-01 01:01')
        myPullRequest.save()

        #proccess the queued pagination
        ProcessGitHubRequest(1)

        # Verify that there are no more queued paginations
        myRequestCaches = GitHubRequestCache.objects.filter(started_at__isnull = True)
        self.assertEqual(myRequestCaches.count(), 0)

    def test_ProcessGitHubRequest(self):
        testRepo = 18295962
        testRepoFullName = 'BenLiyanage/AncientOne'

        #queue some stuff
        QueueGitHubRequest('repos/' + testRepoFullName)
        self.assertEqual(GitHubRequestCache.objects.count(), 1)

        #process some stuff
        ProcessGitHubRequest(1)
        myRequestCaches = GitHubRequestCache.objects.filter(started_at__isnull = True)
        self.assertEqual(myRequestCaches.count(), 0)

if __name__ == '__main__':
    unittest.main()