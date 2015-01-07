# Overview

# Installation

* Pull down this repository.  
* Run the vagrant file.  This will assemble an appropriate box for you.
* Create a mysql database named 'github'
* Replace github api keys in *populargithub/settings/__init__.py--template*

## Requirements

At the moment this application requires mysql--there are some mysql specific queries in it.

## TODO
* Add Pagination Processing for the pull requests.  Currently it only imports the last 30 pull requests that have been closed.
* Parse out Month/Date from pull_request dates on cache so that the application can be database agnostic.
* Automate Database setup
* Log logging to database for Repo Processing to allow for rendering statistical success rates.