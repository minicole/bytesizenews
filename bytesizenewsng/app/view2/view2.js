'use strict';

angular.module('myApp.view2', ['ngRoute'])

    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/view2', {
            templateUrl: 'view2/view2.html',
            controller: 'View2Ctrl'
        });
    }])

    .controller('View2Ctrl', ['$scope', '$http', function ($scope, $http) {
        var config = {headers:  {} };

        $http.get('http://localhost:8001/articles/',config)
            .then(function(response) {
                console.log(response);
                var articlesStringified = response.data;
                var articles = [];
                for (var i = 0; i < articlesStringified.length; i++) {
                    articles.push(JSON.parse(articlesStringified[i]));
                }
                $scope.articles = articles;
            });
    }]);