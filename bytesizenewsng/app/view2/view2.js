'use strict';

angular.module('myApp.view2', ['ngRoute'])

    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/view2', {
            templateUrl: 'view2/view2.html',
            controller: 'View2Ctrl'
        });
    }])

    .controller('View2Ctrl', ['$scope', '$http', function ($scope, $http) {

        $http({
            method: 'POST',
            url: 'http://localhost:8001/articles'
        }).then(function successCallback(parameters) {
            var response = parameters.response;
            // this callback will be called asynchronously
            // when the response is available
            $scope.articles = response.data;

        }, function errorCallback(parameters) {
            var response = parameters.response;
            // called asynchronously if an error occurs
            // or server returns response with an error status.
        });

    }]);