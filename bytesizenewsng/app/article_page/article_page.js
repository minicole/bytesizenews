'use strict';

angular.module('myApp.article_page', ['ngRoute', 'ngProgress','rzModule'])

    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/article_page/:articleid?', {
            templateUrl: 'article_page/article_page.html',
            controller: 'article_pageCtrl'
        });
    }])

    .controller('article_pageCtrl', ['$route', '$http', '$scope', 'ngProgressFactory', function ($route, $http, $scope, ngProgressFactory) {
        $scope.progressbar = ngProgressFactory.createInstance();
        $scope.progressbar.start();
        $scope.slider = {
              value: 50,
              options: {
                floor: 0,
                ceil: 100,
                  readOnly: true,
                  showSelectionBar: true,
                  selectionBarGradient: {
                      from: 'red',
                      to: 'green'
                  },
                  getPointerColor: function(value) {
                    if (value <= 25)
                        return 'red';
                    if (value <= 50)
                        return 'orange';
                    if (value <= 75)
                        return 'yellow';
                    return 'green';
                }
              }
            };
        var config = {headers: {}};
        $scope.rated = false;
        var url = 'http://bytesizenews.net:8080/article/';

        if ($route.current.params.articleid) {
            url += $route.current.params.articleid + '/';
        }

        $http.get(url, config)
            .then(function (response) {
                console.log(response);
                var articleParsed = response.data;

                if (articleParsed.ratings.length > 0) {
                    articleParsed.rated = articleParsed.ratings.find(function (currentValue) {
                        return currentValue.nb_sentences = articleParsed.summary_sentences.length;
                    });
                } else {
                    articleParsed.rated = {
                        nb_thumbs_up: 0,
                        nb_thumbs_down: 0
                    };
                }

                $scope.slider.value = Math.floor(articleParsed.sentiment * 100);

                var date = Date(articleParsed.published_at);
                articleParsed.date = date.substring(0, date.lastIndexOf(":") + 3);
                $scope.progressbar.complete();
                $scope.article = articleParsed;
            });

        $scope.rateThumbsUp = function () {
            if (!$scope.rated) {
                $scope.article.rated.nb_thumbs_up++;
                $scope.rated = true;
                url = "http://bytesizenews.net:8080/thumbsup/" + $route.current.params.articleid + "/" + $scope.article.summary_sentences.length + "/";
                $http.get(url, config)
                    .then(function (response) {
                        console.log(response);
                    });
            }
        };

        $scope.rateThumbsDown = function () {
            if (!$scope.rated) {
                $scope.article.rated.nb_thumbs_down++;
                $scope.rated = true;
                url = "http://bytesizenews.net:8080/thumbsdown/" + $route.current.params.articleid + "/" + $scope.article.summary_sentences.length + "/";
                $http.get(url, config)
                    .then(function (response) {
                        console.log(response);
                    });
            }
        };
    }]);

