'use strict';

angular.module('myApp.article_list', ['ngRoute', 'ngProgress'])

    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/article_list/:category?', {
            templateUrl: 'article_list/article_list.html',
            controller: 'article_listCtrl'
        });
    }])

    .controller('article_listCtrl', ['$scope', '$http', '$route', '$window', '$location', 'ngProgressFactory', function ($scope, $http, $route, $window, $location, ngProgressFactory) {
        $scope.progressbar = ngProgressFactory.createInstance();
        $scope.progressbar.start();
        var randomColor = function() {
            var letters = '0123456789ABCDEF';
            var color = '#';
            for (var i = 0; i < 6; i++ ) {
                color += letters[Math.floor(Math.random() * 16)];
            }
            return color;
        };

        var config = {headers:  {} };
        var url = 'http://bytesizenews.net:8080/articles/';

        if ($route.current.params.category) {
            url += $route.current.params.category.toLowerCase() + '/';
        }

        $http.get(url,config)
            .then(function(response) {
                console.log(response);
                var articlesParsed = response.data;
                var articles = [];
                for (var i = 0; i < articlesParsed.length; i++) {
                    var article = articlesParsed[i];
                    if (article.url_to_image) {
                        article.background = "background-image: url(" + article.url_to_image + ")";
                    } else {
                        article.background = "background-color: " + randomColor();
                    }
                    var d = new Date(article.published_at);
                    article.hours = Math.floor((Date.now() - d.getTime()) / 1000 / 60 / 60);
                    articles.push(article);
                }
                $scope.progressbar.complete();
                $scope.articles = articles;
            });

        $scope.goToArticle = function(articleid) {
            var newUrl = $location.$$absUrl.substring(0, $location.$$absUrl.indexOf("/#!/")) + "/#!/article_page/" + articleid;
            if ($scope.$$phase)
                $window.location.href = newUrl;
            else {
                $location.path(newUrl);
                $scope.$apply();
            }
        }
    }]);