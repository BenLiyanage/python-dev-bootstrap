function formatGitHubDate(gitHubDate)
{
    resetDate = new Date(gitHubDate * 1000)
    minutes = resetDate.getMinutes()
    if (minutes < 10)
    {
        minutes = "0" + minutes;
    }
    dateString = 
        resetDate.getMonth() + '/' + resetDate.getDate() + '/' + resetDate.getFullYear() 
        + ' ' + 
        resetDate.getHours() % 12 + ':' + minutes
    return dateString
}

var githubApp = angular.module('githubApp', [])
githubApp.controller('searchCtrl', function($scope, $http) {
    $scope.selectedRepo = []
    $scope.isNumber = angular.isNumber;
    
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
        console.log(index)
        if (index >= 0)
        {   
            $scope.selectedRepo.splice(index, 1)
        }
    }
});
githubApp.directive('autoComplete', function($timeout, $http)
    {
        return function (scope, iElement, iAttrs)
            {
                iElement.autocomplete({
                    minLength: 0,
                    source: function(request, response) { 
                            //need to do the dynamic search here using "term" as the current input
                            //alert('hi')
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
                            scope['selectedRepo'].push({'full_name': ui.item.full_name})
                            scope.$apply();
                        }
                    })
                .data('ui-autocomplete')._renderItem = function(ul, item) {
                        return $("<li></li>")
                                    .data("item.autocomplete", item)
                                    .append("<a>" + item.full_name + "</a>")
                                    .appendTo(ul)
                        
                    }
            }
    }
);