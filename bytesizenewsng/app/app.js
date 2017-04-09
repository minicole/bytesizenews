"use strict";

// Declare app level module which depends on views, and components
angular.module('myApp', [
  'ngRoute',
  'myApp.article_page',
  'myApp.article_list',
  'myApp.version'
]).
config(['$locationProvider', '$routeProvider', function($locationProvider, $routeProvider) {
  $locationProvider.hashPrefix('!');

  $routeProvider.otherwise({redirectTo: '/article_list'});
}]);
