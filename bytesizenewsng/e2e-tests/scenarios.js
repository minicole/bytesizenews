'use strict';

/* https://github.com/angular/protractor/blob/master/docs/toc.md */

describe('my app', function() {


  it('should automatically redirect to /article_page when location hash/fragment is empty', function() {
    browser.get('index.html');
    expect(browser.getLocationAbsUrl()).toMatch("/article_page");
  });


  describe('article_page', function() {

    beforeEach(function() {
      browser.get('index.html#!/article_page');
    });


    it('should render article_page when user navigates to /article_page', function() {
      expect(element.all(by.css('[ng-view] p')).first().getText()).
        toMatch(/partial for view 1/);
    });

  });


  describe('article_list', function() {

    beforeEach(function() {
      browser.get('index.html#!/article_list');
    });


    it('should render article_list when user navigates to /article_list', function() {
      expect(element.all(by.css('[ng-view] p')).first().getText()).
        toMatch(/partial for view 2/);
    });

  });
});
