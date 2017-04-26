'use strict';

angular.module('myApp.article_page', ['ngRoute', 'ngProgress', 'rzModule'])

    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/article_page/:articleid?', {
            templateUrl: 'article_page/article_page.html',
            controller: 'article_pageCtrl'
        });
    }])

    .controller('article_pageCtrl', ['$route', '$http', '$scope', 'ngProgressFactory', '$window', '$location', function ($route, $http, $scope, ngProgressFactory, $window, $location) {

        var randomColor = function () {
            var letters = '0123456789ABCDEF';
            var color = '#';
            for (var i = 0; i < 6; i++) {
                color += letters[Math.floor(Math.random() * 16)];
            }
            return color;
        };

        $scope.progressbar = ngProgressFactory.createInstance();
        $scope.progressbar.setHeight("5px");
        $scope.progressbar.setColor("#f04641");
        $scope.progressbar.start();
        $scope.data_loaded = false;
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
                getPointerColor: function (value) {
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

        $scope.slider_compression = {
            value: 50,
            options: {
                floor: 0,
                ceil: 100,
                readOnly: true
            }
        };
        var config = {headers: {}};
        $scope.rated = false;
        var url = 'http://bytesizenews.net:8080/article/';

        if ($route.current.params.articleid) {
            url += $route.current.params.articleid + '/';
        }

        function decodeHtml(html) {
            html = html.replace(/&quot;/g, '\'');
            var txt = document.createElement("textarea");
            txt.innerHTML = html;
            return txt.value;
        }

        $http.get(url, config)
            .then(function (response) {
                console.log(response);
                var articleParsed = response.data;
                articleParsed = JSON.stringify(articleParsed);
                articleParsed = decodeHtml(articleParsed);
                articleParsed = JSON.parse(articleParsed);

                if (articleParsed.summary_sentences === undefined || articleParsed.summary_sentences.length === 0) {
                    $scope.articleIsSummarized = false;
                } else {
                    $scope.articleIsSummarized = true;
                    if (articleParsed.summary_sentences[articleParsed.summary_sentences.length - 1] === "") {
                        articleParsed.summary_sentences.pop();
                    }
                    if (articleParsed.ratings.length > 0) {
                        articleParsed.rated = articleParsed.ratings[articleParsed.ratings.length - 1];
                        // articleParsed.rated = articleParsed.ratings.find(function (currentValue) {
                        //     return currentValue.nb_sentences = articleParsed.summary_sentences.length;
                        // });
                        if (articleParsed.nb_original_chars && articleParsed.rated.nb_summarized_chars) {
                            articleParsed.compression = 100 - Math.floor(articleParsed.rated.nb_summarized_chars / articleParsed.nb_original_chars * 100);
                            $scope.slider_compression.value = articleParsed.compression;
                        } else {
                            articleParsed.compression = "unknown";
                            $scope.slider_compression.value = 0;
                        }
                    } else {
                        articleParsed.rated = {
                            nb_thumbs_up: 0,
                            nb_thumbs_down: 0
                        };
                        articleParsed.compression = "unknown";
                        $scope.slider_compression.value = 0;
                    }
                }

                if (articleParsed.similar_articles !== undefined) {
                    var articles = [];
                    if (articleParsed.similar_articles && articleParsed.similar_articles.length !== 0) {
                        articleParsed.similar_articles = JSON.parse(articleParsed.similar_articles);
                        if (typeof articleParsed.similar_articles === "object") {
                            for (var i = articleParsed.similar_articles.length - 1; i >= 0; i--) {
                                var article = articleParsed.similar_articles[i];
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
                                    article.hours = Math.floor(time / 60 / 24) + " days since posted";
                                }
                                if (article.description === undefined || article.description === "") {
                                    article.description = "no description";
                                }
                                articles.push(article);
                            }
                        }
                    }
                    articleParsed.similar_articles = articles;
                }

                $scope.slider.value = Math.floor(articleParsed.sentiment * 100);

                if (articleParsed.published_at !== undefined) {
                    var date = new Date(articleParsed.published_at.$date);
                    articleParsed.date = date.toDateString() + " - " + date.toLocaleTimeString();
                }
                $scope.progressbar.complete();
                $scope.data_loaded = true;
                $scope.article = articleParsed;
            });

        $scope.rateThumbsUp = function () {
            if (!$scope.rated) {
                $scope.article.rated.nb_thumbs_up++;
                $scope.rated = true;
                url = "http://bytesizenews.net:8080/thumbsup/" + $scope.article.rated._id.$oid + "/" + $scope.article.summary_sentences.length + "/";
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
                url = "http://bytesizenews.net:8080/thumbsdown/" + $scope.article.rated._id.$oid + "/" + $scope.article.summary_sentences.length + "/";
                $http.get(url, config)
                    .then(function (response) {
                        console.log(response);
                    });
            }
        };

        $scope.goToArticle = function (articleid) {
            var newUrl = $location.$$absUrl.substring(0, $location.$$absUrl.indexOf("/#!/")) + "/#!/article_page/" + articleid;
            if ($scope.$$phase)
                $window.location.href = newUrl;
            else {
                $location.path(newUrl);
                $scope.$apply();
            }
        };

        $scope.$on("$destroy", function () {
            if ($scope.progressbar.status() < 1) {
                $scope.progressbar.complete();
            }
        });

    }]);

