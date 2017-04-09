'use strict';

angular.module('myApp.article_list', ['ngRoute'])

    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/article_list/:category?', {
            templateUrl: 'article_list/article_list.html',
            controller: 'article_listCtrl'
        });
    }])

    .controller('article_listCtrl', ['$scope', '$http', '$route', function ($scope, $http, $route) {
        var config = {headers:  {} };
        var url = 'http://bytesizenews.net:8080/articles/';

        if ($route.current.params.category) {
            url += $route.current.params.category.toLowerCase() + '/';
        }

        $http.get(url,config)
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