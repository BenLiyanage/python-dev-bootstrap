var githubApp = angular.module('githubApp')

githubApp.controller('queueMonitorController', function($scope, $http, $interval) {
    $scope.unprocessed = 0
    $scope.successful = 0
    $scope.failed = 0
    
    $scope.updateQueueMonitor = function() {
        $scope.unprocessed = 0
        $scope.successful = 0
        $scope.failed = 0
        
        $http({
            method: 'get',
            url: '/queuemonitordata'
        }).success(function(data, status, headers, config) {
            $scope.unprocessed = data.unproccessed;
            $scope.successful = data.successful;
            $scope.failed = data.failed;
        }).error(function (data, status, headers, config) { console.log(data, status, headers, config) } )
    }
    
    $scope.updateQueueMonitor();
    // this 5 second timer is unnecessarily pounding our server
    $interval(function () { $scope.updateQueueMonitor(); }, 5000)
})