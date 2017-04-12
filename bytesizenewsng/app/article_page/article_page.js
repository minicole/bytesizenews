'use strict';

angular.module('myApp.article_page', ['ngRoute', 'ngProgress','rzModule'])

    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/article_page/:articleid?', {
            templateUrl: 'article_page/article_page.html',
            controller: 'article_pageCtrl'
        });
    }])

    .controller('article_pageCtrl', ['$route', '$http', '$scope', 'ngProgressFactory', function ($route, $http, $scope, ngProgressFactory) {

        var randomColor = function() {
            var letters = '0123456789ABCDEF';
            var color = '#';
            for (var i = 0; i < 6; i++ ) {
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

                if (articleParsed.summary_sentences === undefined) {
                    articleParsed.summary_sentences = articleParsed.description;
                } else {
                    if (articleParsed.summary_sentences[articleParsed.summary_sentences.length - 1] === "") {
                        articleParsed.summary_sentences.pop();
                    }
                    if (articleParsed.ratings.length > 0) {
                        articleParsed.rated = articleParsed.ratings.find(function (currentValue) {
                            return currentValue.nb_sentences = articleParsed.summary_sentences.length;
                        });
                        if (articleParsed.nb_original_chars && articleParsed.rated.nb_summarized_chars) {
                            articleParsed.compression = 100 - Math.floor(articleParsed.rated.nb_summarized_chars / articleParsed.nb_original_chars * 100) + "%";
                        } else {
                            articleParsed.compression = "unknown";
                        }
                    } else {
                        articleParsed.rated = {
                            nb_thumbs_up: 0,
                            nb_thumbs_down: 0
                        };
                        articleParsed.compression = "unknown";
                    }
                }

                var articles = [];
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
                        article.hours = Math.floor((Date.now() - d.getTime()) / 1000 / 60 / 60);
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
                }

                articleParsed.similar_articles = articles;

                $scope.slider.value = Math.floor(articleParsed.sentiment * 100);

                var date = new Date(articleParsed.published_at.$date);
                articleParsed.date = date.toDateString() + " - " + date.toLocaleTimeString();
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
    }]);

