# Overview

When choosing between different technical solutions in the open source world having a vibrant community backing the project can make the difference between a ful rewrite of your application, and a simple upgrade when maintaining your own systems.

This application allows you to compare stats about different publically available github repositories.  Currently it is only comparing pull request rate.  Having current pull requests is an indicator that a repository is actively being maintained. Additional stats will be added at a later time like ticket reclosure rate, and number of contributors.

## Technologies Used

This is a full stack solution.  Technologies I have used in this project are:

* Frontend
    * Angular.js, cause it's cool.
    * Bootstrap, ditto.
    * jQuery, for dropdowns.
    * Google Graph API, cause I didn't realize I should be playing with d3.js
    * Jasmine, for Angular Unit Testing
* Backend
    * Python
    * Django
    * MySQL
    * Github API

# Installation

* Pull down this repository.  
* Run the vagrant file.  This will assemble an appropriate box for you.
* Create a mysql database named 'github' - create database github;
* mkdir /projects/populargithub/logfile
* pip install requirements.txt
* python manage.py makemigrations
* python manage.py migrate
* cp /projects/populargithub/settings/__init__.py--template /projects/populargithub/settings/__init__.py
* set up github api secrets
    * log into github -> https://github.com/settings/applications
    * ->Register New Application
    * ->Fill out Information
    * Put ClientID and Client Secret into __init__.py

How to run:
python manage.py runserver 0.0.0.0:8000 

Web site should be running on 192.168.33.10:8000

## Requirements

At the moment this application requires mysql--there are some mysql specific queries in it.

# TODO
* Add Pagination Processing for the pull requests.  Currently it only imports the last 30 pull requests that have been closed.
* Parse out Month/Date from pull_request dates on cache so that the application can be database agnostic.
* Automate Database setup
* Log logging to database for Repo Processing to allow for rendering statistical success rates.
* Mobile testing.
* Throw in a D3.js example.
* Add heroku toolbelt to vagrant file
* add heroku pluggin: https://github.com/ddollar/heroku-push
* set up web test runner for python: http://tungwaiyip.info/software/HTMLTestRunner.html