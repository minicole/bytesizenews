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

        var searching = false;

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
                "key": "last 6 hours",
                "hours": 6,
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
            },
            {
                "key": "last 7 days",
                "hours": 0,
                "days": 7
            },
            {
                "key": "last 30 days",
                "hours": 0,
                "days": 30
            },
            {
                "key": "last year",
                "hours": 0,
                "days": 365
            }
        ];
        $scope.selectedTime = $scope.timeOptions[5].key;

        var processArticles = function (response) {
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
                    var time = Math.floor(article.timeSince / 1000 / 60);
                    if (time <= 0) {
                        article.hours = "Just now"
                    } else if (time < 60) {
                        article.hours = time + " minutes since posted";
                    } else if (Math.floor(time / 60) < 24) {
                        article.hours = Math.floor(time / 60) + " hours since posted";
                    } else if (Math.floor(time / 60 / 24) < 365) {
                        article.hours = Math.floor(time / 60 / 24) + " years since posted";
                    }
                    if (article.description === undefined || article.description === "") {
                        article.description = "no description";
                    }
                    articles.push(article);
                }

                var articlesSorted = articles.sort(function (item1, item2) {
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

        $scope.showPrev = function () {
            return parseInt($scope.page_nb) > 1;
        };

        $scope.goToNextPrevPage = function (pageDirection) {
            var page = parseInt($scope.page_nb) + pageDirection;
            $scope.page_nb = page;

            var newUrl = "";

            if (searching) {
                var newUrl = "http://bytesizenews.net:8080/search/";
                // var newUrl = $location.$$absUrl.substring(0, $location.$$absUrl.indexOf("/#!/")) + ":8080/search/";
                newUrl += $scope.page_nb + "/";
                if ($scope.selectedTime) {
                    newUrl += $scope.selectedTime.hours + "/";
                    newUrl += $scope.selectedTime.days + "/";
                } else {
                    newUrl += 0 + "/";
                    newUrl += 0 + "/";
                }
                newUrl += encodeURI($scope.search_query) + "/";
                $scope.progressbar.start();
                $http({method: 'GET', url: newUrl}).success(function (data, status, headers, config) {
                    processArticles(data);
                    $window.scrollTo(0, 0);
                });
            } else {
                // newUrl = $location.$$absUrl.substring(0, $location.$$absUrl.indexOf("/#!/")) + ":8080/articles/";
                newUrl = "http://bytesizenews.net:8080/articles/";
                newUrl += page + "/";
                if ($route.current.params.category) {
                    newUrl += $route.current.params.category.toLowerCase() + '/';
                }
                $scope.progressbar.start();
                $http({method: 'GET', url: newUrl}).success(function (data, status, headers, config) {
                    processArticles(data);
                    $window.scrollTo(0, 0);
                });
            }
        };

        $scope.$on("$destroy", function () {
            if ($scope.progressbar.status() < 1) {
                $scope.progressbar.complete();
            }
        });

        $scope.performSearch = function () {
            if ($scope.search_form.query.$valid) {
                var query = "http://bytesizenews.net:8080/search/";
                query += $scope.page_nb + "/";
                if ($scope.selectedTime) {
                    query += $scope.selectedTime.hours + "/";
                    query += $scope.selectedTime.days + "/";
                } else {
                    query += 0 + "/";
                    query += 0 + "/";
                }
                searching = true;
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
}).directive('bsDropdown', function ($compile) {
    return {
        restrict: 'E',
        scope: {
            items: '=dropdownData',
            doSelect: '&selectVal',
            selectedItem: '=preselectedItem'
        },
        link: function (scope, element, attrs) {
            var html = '';
            switch (attrs.menuType) {
                case "button":
                    html += '<div class="btn-group"><button class="button-label btn nicole-copy-mike-button" myOnKeyDownCall="performSearch()">Time Span</button><button class="btn dropdown-toggle nicole-copy-mike-button" data-toggle="dropdown"><span class="caret"></span></button>';
                    break;
                default:
                    html += '<div class="dropdown"><a class="dropdown-toggle" role="button" data-toggle="dropdown"  href="javascript:;">Time Span<b class="caret"></b></a>';
                    break;
            }

            html += '<ul class="dropdown-menu nicole-copy-mike-button"><li ng-repeat="item in items"><a tabindex="-1" data-ng-click="selectVal(item)">{{item.key}}</a></li></ul></div>';
            element.append($compile(html)(scope));
            for (var i = 0; i < scope.items.length; i++) {
                if (scope.items[i].key === scope.selectedItem) {
                    scope.bSelectedItem = scope.items[i];
                    break;
                }
            }
            scope.selectVal = function (item) {
                switch (attrs.menuType) {
                    case "button":
                        $('button.button-label', element).html(item.key);
                        break;
                    default:
                        $('a.dropdown-toggle', element).html('<b class="caret"></b> ' + item.key);
                        break;
                }
                scope.doSelect({
                    selectedVal: item
                });
            };
            scope.selectVal(scope.bSelectedItem);
        }
    };
});


