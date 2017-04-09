'use strict';

angular.module('myApp.article_page', ['ngRoute'])

    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/article_page/:articleid?', {
            templateUrl: 'article_page/article_page.html',
            controller: 'article_pageCtrl'
        });
    }])

    .controller('article_pageCtrl', ['$route', '$http', function ($route, $http) {
        var config = {headers: {}};
        var url = 'http://bytesizenews.net:8080/article/';

        if ($route.current.params.articleid) {
            url += $route.current.params.articleid + '/';
        }

        $http.get(url, config)
            .then(function (response) {
                console.log(response);
                var articleParsed = JSON.parse(response.data);

                articleParsed.rated = articleParsed.rating.find(nb_sentences == articleParsed.summary_sentences.length);
                $scope.article = articleParsed;
            });
    }]);