google.load("visualization", "1", {packages:["corechart"]});
var githubApp = angular.module('githubApp', [])

function formatGitHubDate(gitHubDate)
{
    resetDate = new Date(gitHubDate * 1000)
    minutes = resetDate.getMinutes()
    if (minutes < 10)
    {
        minutes = "0" + minutes;
    }
    dateString = 
        (resetDate.getMonth() + 1) + '/' + resetDate.getDate() + '/' + resetDate.getFullYear() 
        + ' ' + 
        resetDate.getHours() % 12 + ':' + minutes
    return dateString
}

githubApp.controller('compareController', function($scope, $http, $timeout) {
    $scope.selectedRepo = [{full_name: 'sevenwire/forgery', id: 322 }, {full_name: 'collectiveidea/acts_as_geocodable', id: 364 }]
    
    //Update Rate Limit For Search Stats
    $http({
        method: 'get', 
        url: 'https://api.github.com/rate_limit'
    })
        .success(function(data, status, headers, config) {
            $scope.rateLimit = data.resources.search.limit
            $scope.rateLimitRemaining = data.resources.search.remaining
            $scope.rateLimitReset = formatGitHubDate(data.resources.search.reset)
        })
        .error(function() {})
        
    $scope.remove = function(item) {
        var index = $scope.selectedRepo.indexOf(item)
        if (index >= 0)
        {   
            $scope.selectedRepo.splice(index, 1)
        }
    }
    
    $scope.updateChart = function(iElement) {
        var full_names = ''    
        $scope.selectedRepo.forEach(function(repo)
        {
            full_names = full_names + repo.full_name + '+'
        })
        
        //remove trailing plus
        full_names = full_names.substr(0, full_names.length-1)
        
        $http({
            method: 'get',
            url: '/comparedata',
            params: { 'full_names': full_names}
        }).success(function(data, status, headers, config) {
            var chartData = new google.visualization.DataTable(data);
            var mergesOptions = {
                title: 'Code Merges Per Month',
                chartArea: {left:30, width:'70%'}
            };
            var chart_MergesPerMonth = new google.visualization.LineChart(iElement[0]);
            chart_MergesPerMonth.draw(chartData, mergesOptions);
        }).error(function (data, status, headers, config) { console.log(data, status, headers, config) } )
    }
});

githubApp.directive('mergesGraph', function() {
    return function(scope, iElement) {
        scope.$watch('selectedRepo', function() {
            scope.updateChart(iElement) 
        },true)
    }
})

githubApp.directive('autoComplete', function($http) {
    return function (scope, iElement, iAttrs)
        {
            iElement.autocomplete({
                minLength: 0,
                source: function(request, response) { 
                    //need to do the dynamic search here using "term" as the current input
                    var req = { 
                        method: 'get', 
                        url: 'https://api.github.com/search/repositories',
                        params: { q: request.term }
                    }
                    $http(req)
                        .success(function(data, status, headers, config) { 
                            scope['rateLimit'] = headers('X-RateLimit-Limit');
                            scope['rateLimitRemaining'] = headers('X-RateLimit-Remaining');
                            scope['rateLimitReset'] = formatGitHubDate(headers('X-RateLimit-Reset'))
                            response(data.items); 
                        })
                        .error(function() { response() })
                },
                select: function(event, ui) {
                    scope['selectedRepo'].push({'full_name': ui.item.full_name, id: ui.item.id})
                    scope.$apply();
                }
            }).data('ui-autocomplete')._renderItem = function(ul, item) {
                return $("<li></li>")
                            .data("item.autocomplete", item)
                            .append("<a>" + item.full_name + "</a>")
                            .appendTo(ul)
                
            }
        }
});