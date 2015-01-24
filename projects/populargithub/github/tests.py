from django.test import TestCase
from models import Repo
from processing import ProcessRepo
from django.db.models.base import ObjectDoesNotExist

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
        
    def test_PrcoessRepoLargePullRequestCount(self):
        testRepo = 3638964
        testRepoFullName = 'ansible/ansible'

        # Proccess a known repo
        ProcessRepo(testRepoFullName)
        
        # test some default values
        myRepo = Repo.objects.get(pk = testRepo)
        
        self.assertEqual(myRepo.full_name, testRepoFullName)
        
        # test that pull requests got imported
        # this repo should have more than 100 pull requests.
        # importing pull requests requires pagingation to go over 100 entries
        self.assertGreater(myRepo.pullrequest_set.count(), 100)

        
if __name__ == '__main__':
    unittest.main()