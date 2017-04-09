'use strict';

angular.module('myApp.article_page', ['ngRoute'])

    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/article_page/:articleid?', {
            templateUrl: 'article_page/article_page.html',
            controller: 'article_pageCtrl'
        });
    }])

    .controller('article_pageCtrl', [function () {
        var config = {headers: {}};
        var url = 'http://bytesizenews.net:8080/articles/';

        if ($route.current.params.category) {
            url += $route.current.params.category.toLowerCase() + '/';
        }

        $http.get(url, config)
            .then(function (response) {
                console.log(response);
                var articlesParsed = JSON.parse(JSON.parse(response.data));
                var articles = [];
                for (var i = 0; i < articlesParsed.length; i++) {
                    var article = articlesParsed[i];
                    if (article.url_to_image) {
                        article.background = "background-image: url(" + article.url_to_image + ")";
                    } else {
                        article.background = "background-color: " + randomColor();
                    }
                    articles.push(article);
                }

                $scope.articles = articles;
            });
    }]);