'use strict';

angular.module('myApp.article_list', ['ngRoute', 'ngProgress'])

    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/article_list/:category?/:page_nb?/', {
            templateUrl: 'article_list/article_list.html',
            controller: 'article_listCtrl'
        })
    }])
    .controller('article_listCtrl', ['$scope', '$http', '$route', '$window', '$location', 'ngProgressFactory', function ($scope, $http, $route, $window, $location, ngProgressFactory) {
        $scope.progressbar = ngProgressFactory.createInstance();
        $scope.progressbar.setHeight("5px");
        $scope.progressbar.setColor("#f04641");
        $scope.progressbar.start();
        var randomColor = function () {
            var letters = '0123456789ABCDEF';
            var color = '#';
            for (var i = 0; i < 6; i++) {
                color += letters[Math.floor(Math.random() * 16)];
            }
            return color;
        };

        var config = {headers: {}};
        var url = 'http://bytesizenews.net:8080/articles/';

        if ($route.current.params.page_nb) {
            url += $route.current.params.page_nb + '/';
            $scope.page_nb = $route.current.params.page_nb;
        } else {
            url += 1 + '/';
            $scope.page_nb = 1;
        }
        if ($route.current.params.category && $route.current.params.category !== "all") {
            url += $route.current.params.category.toLowerCase() + '/';
        }
        $scope.loaded = false;

        $scope.timeOptions = [
            {
                "key": "last hour",
                "hours": 1,
                "days": 0
            },
            {
                "key": "last 5 hours",
                "hours": 5,
                "days": 0
            },
            {
                "key": "last 12 hours",
                "hours": 12,
                "days": 0
            },
            {
                "key": "last day",
                "hours": 0,
                "days": 1
            },
            {
                "key": "last 3 days",
                "hours": 0,
                "days": 3
            }
        ];

        var processArticles = function(response) {
            console.log(response);
                var articlesParsed = response.articles;
                $scope.hasNextPage = response.hasNextPage;
                var articles = [];
                if (typeof articlesParsed === "object") {
                    $scope.hasArticles = true;
                    for (var i = articlesParsed.length - 1; i >= 0; i--) {
                        var article = articlesParsed[i];
                        if (article.url_to_image) {
                            article.background = "background-image: url(" + article.url_to_image + ")";
                        } else {
                            article.background = "background-color: " + randomColor();
                        }
                        var d = new Date(article.published_at);
                        var now = new Date().getTime();
                        article.timeSince = now - d.getTime();
                        article.hours = Math.floor(article.timeSince / 1000 / 60 / 60);
                        if (article.hours <= 0) {
                            article.hours = "Just now";
                        } else {
                            article.hours = article.hours + " hours since posted";
                        }
                        if (article.description === undefined || article.description === "") {
                            article.description = "no description";
                        }
                        articles.push(article);
                    }

                    var articlesSorted = articles.sort(function(item1, item2) {
                        if (item1.timeSince < item2.timeSince) return -1;
                        if (item1.timeSince > item2.timeSince) return 1;
                        return 0;
                    });
                } else {
                    $scope.hasArticles = false;
                }
                $scope.loaded = true;
                $scope.progressbar.complete();
                $scope.articles = articlesSorted;
        };

        $http.get(url, config)
            .then(function (response) {
                processArticles(response.data);
            });

        $scope.goToArticle = function (articleid) {
            var newUrl = $location.$$absUrl.substring(0, $location.$$absUrl.indexOf("/#!/")) + "/#!/article_page/" + articleid;
            if ($scope.$$phase)
                $window.location.href = newUrl;
            else {
                $location.path(newUrl);
                $scope.$apply();
            }
        };

        $scope.showPrev = function() {
            return parseInt($scope.page_nb) > 1;
        };

        $scope.goToNextPrevPage = function (pageDirection) {
            var page = parseInt($scope.page_nb) + pageDirection;
            var newUrl = $location.$$absUrl.substring(0, $location.$$absUrl.indexOf("/#!/")) + "/#!/article_list/";
            if ($route.current.params.category) {
                newUrl += $route.current.params.category.toLowerCase() + '/';
            } else {
                newUrl += "all/"
            }
            newUrl += page + "/";
            if ($scope.$$phase)
                $window.location.href = newUrl;
            else {
                $location.path(newUrl);
                $scope.$apply();
            }
        };

        $scope.$on("$destroy", function () {
            $scope.progressbar.complete();
        });

        $scope.performSearch= function() {
            if ($scope.search_form.query.$valid && $scope.search_form.date.$valid) {
                var query = "http://bytesizenews.net:8080/search/";
                query += $scope.page_nb + "/";
                if ($scope.search_date) {
                    var timeQuery = JSON.parse($scope.search_date);
                    query += timeQuery.hours + "/";
                    query += timeQuery.days + "/";
                } else {
                    query += 0 + "/";
                    query += 0 + "/";
                }
                query += encodeURI($scope.search_query) + "/";
                $http({method: 'GET', url: query}).success(function (data, status, headers, config) {
                    processArticles(data);
                });
            }
        }
    }]).directive('myOnKeyDownCall', function () {
    return function (scope, element, attrs) {
        element.bind("keydown keypress", function (event) {
            if (event.keyCode == 13) {
                scope.$apply(function () {
                    scope.$eval(attrs.myOnKeyDownCall);
                });
                event.preventDefault();
            }
        });
    };
});


