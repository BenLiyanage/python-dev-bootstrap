# Wikipedia Drug Scraper



## Setup and Usage

* `pip install -r requirements.txt`
* From the `drugscraper` folder run: `scrapy crawl DrugScraper` to get the data.
* From the `web` folder run: `FLASK_APP=web.py flask run` to run the web server.
* To view the site go to `http://localhost:5000/`.  This site is super primative.


## Stats on Half-Life

Most half life's were in the form of a range.  I normalized all the data to be measured in seconds while parsing the
data, and did the min/max/average on the lower and upper bound of the range in excel.  When a half life was not given
as a range, I used the provided value as both th emin and max.  I did some light cleanup
in excel for some formats that my regex didn't match quite well since it was easier then coding more.

|           |lower bound half life  | upper bound half life |
|-----------|-----------------------|-----------------------|
| MIN	    | 30	                | 30                    |
| MAX	    | 11664000	            | 15292800              |
| AVERAGE	| 595972.898	        | 738104.5714           |


About 33% of the drugs had a drug code present (70 out of ~212).

About 1.5% had the drug classification present. Drug clasification data could most likely be pulled from the categories.

The drug classes found included:

* CNS stimulant
* Local anesthetic
* CNS stimulant
* immunosuppressant
* calcineurin inhibitor
* eye medication

## Modeling the data

In a relational database I would model the data something like this:

| Drug          |           |
|---------------|-----------|
| id            | int       |
| name          | varchar   |
| wiki_url      | varchar   |
| html          | blob      |

| DrugProperty  |           |
|---------------|-----------|
| id            | int       |
| name          | varchar   |
| value         | varchar   |
| category      | varchar   | -- this would be used to track the header from the infobox on wikipedia.

This layout would give us the flexibility to track additional properties as they are discovered, without having
to redesign the schema every time.

# Origianl Requirements Below

# Data Engineering Project

This project is intended to test some common Data Engineering tasks, including crawling, data wrangling and structuring of data. The goal is to gather information about the properties of drugs from Wikipedia, structure that data so it can be used for further analysis, and provide some basic statistics about the data.

The category in Wikipedia can be found here:

    https://en.wikipedia.org/wiki/Category:Drugs_by_target_organ_system

An example of a drug from one of the subcategories is:

    https://en.wikipedia.org/wiki/Omeprazole

## Requirements

1) Download all the source data from Wikipedia

2) Structure the data hierarchically in a logical directory structure

3) The source HTML data for each page should be stored in the directory structure

4) There should be a JSON file for each of the drugs in the directory structure that contains the data from the data
tables on each of the wiki pages.  eg, for Omzeprazole above, the data for all of the sections in the table on the right
hand side ("Clinical data", "Legal Status", "Pharmacokinetic data", etc) should be represented in the JSON file.  This
JSON file should also contain the URL of the source data.

5) Based on the data retrieved, provide some simple stats:

- Biological half-life: max, min, average
- Percentage of drugs that have a DrugBank code
- The drug classes found

6) Provide a sample database schema for a "drugs" table (or tables, if appropriate)

7) Provide a simple Flask server that can serve up this data


## Deliverable

A zip file, containing:

1) The code that you used to do the downloading
2) The directory structure mentioned above
3) A CSV file containing the exported data
4) A README file that contains:
    - The stats from requirement #5 above
    - The DB schema from requirement #6 above


## Notes

- Your code should be written in Python 3. It can be in the form of standalone code or a Jupyter Notebook.
- The code for downloading should be parallelized (multi-process / multi-threaded)

