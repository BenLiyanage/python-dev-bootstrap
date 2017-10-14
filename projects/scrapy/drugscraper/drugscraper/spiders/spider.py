import json
import os
import re

import scrapy
from bs4 import BeautifulSoup


class Drugs(scrapy.Spider):
    name = "DrugScraper"
    filemask = "./data/{}/{}"

    # Constants for file position
    HALF_LIFE = 0
    DRUG_BANK = 1
    DRUG_CLASS = 2
    HALF_LIFE_MIN = 3
    HALF_LIFE_MAX = 4

    custom_settings = {
        'DEPTH_LIMIT': 2,
        'CONCURRENT_REQUESTS': 16,
    }

    def start_requests(self):
        try:
            os.remove('stats.csv')
        except FileNotFoundError:
            pass

        urls = [
            'https://en.wikipedia.org/wiki/Category:Drugs_by_target_organ_system'
            # 'https://en.wikipedia.org/wiki/Omeprazole'
            # 'https://en.wikipedia.org/wiki/Vemurafenib'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if 'Category' in response.url:
            # Need to return the yielded list of URLs, if it exists.
            return self.parse_category(response)
        else:
            self.parse_drug(response)

    def parse_category(self, response):
        # self.log(response.css('.mw-category a').extract())
        for a in response.css('.mw-category a'):
            yield response.follow(a, callback=self.parse)

    def parse_drug(self, response):
        drug_name = response.url.split('/')[-1]

        self.save_string(drug_name, response.text, 'page.html')
        self.save_json(response, drug_name)

    def save_json(self, response, drug_name):
        # Loop over the rows of the info box

        stats = [''] * 6
        infobox = {}
        data = {
            'url': response.url,
            'infobox': infobox
        }

        section_header = None
        for item in (response.css('.infobox tr')):
            header_fingerprint = item.css('th::attr(style)').extract_first()
            if header_fingerprint == 'text-align:center;background:#ddd':
                # returns an array of text, so lets make it a single string.
                section_header = BeautifulSoup(item.extract(), 'lxml').get_text().strip()
            else:
                raw_link_title = item.css('th').extract_first()

                # This is skipping the chemical diagram
                if not raw_link_title:
                    continue

                link_title = BeautifulSoup(item.css('th').extract_first(), 'lxml').get_text()
                raw_value = '$$$'.join(item.css('td').extract())
                value = BeautifulSoup(raw_value, 'lxml').get_text().strip()
                infobox[link_title] = {'value': value, 'raw': raw_value, 'section_header': section_header}

                if link_title == 'Biological half-life':
                    stats[self.HALF_LIFE] = value
                    stats[self.HALF_LIFE_MIN], stats[self.HALF_LIFE_MAX] = self.parse_halflife(value)
                elif link_title == 'DrugBank':
                    stats[self.DRUG_BANK] = value
                elif link_title == 'Drug class':
                    stats[self.DRUG_CLASS] = value

        # Using this as a fingerprint for this being a page about a drug...
        # Probably not the best fingerprint, but it works ok given the small scope.
        if len(infobox.keys()):
            self.save_string(drug_name, json.dumps(data), 'data.json')
            with open('./stats.csv', 'a') as stats_file:
                stats_file.write('"{}","{}"\n'.format('","'.join(stats), response.url))

    @staticmethod
    def save_string(drug_name, string, filename):
        drug_folder = './data/{}'.format(drug_name)
        drug_filename = '{}/{}'.format(drug_folder, filename)
        os.makedirs(drug_folder, exist_ok=True)
        with open(drug_filename, 'w') as drug_file:
            drug_file.write(string)

    @classmethod
    def parse_halflife(cls, string):
        # any ranges, aka `1-3 hours`
        range_match = r"([\d]+\.?[\d]*)[^\d\.]+([\d]+\.?[\d]*)(.+)"

        match = re.match(range_match, string)
        if match:
            unit = cls.parse_unit(match.group(3))

            return (
                cls.parse_seconds_from_time(match.group(1), unit),
                cls.parse_seconds_from_time(match.group(2), unit),
            )

        # any single times, aka `1 hour`
        single_match = r"([\d]+\.?[\d]*)(.+)"
        match = re.match(single_match, string)
        if match:
            unit = cls.parse_unit(string)
            seconds = cls.parse_seconds_from_time(match.group(1), unit)
            return (
                seconds,
                seconds,
            )

        # Don't really know the format, lets just move on
        return "", ""

    @staticmethod
    def parse_unit(string):
        units = [
            {'name': 'minuetes', 'value': 'minuetes'},
            {'name': 'min', 'value': 'minuetes'},
            {'name': 'days', 'value': 'days'},
            {'name': 'seconds', 'value': 'seconds'},
            {'name': 'hours', 'value': 'hours'},
            {'name': 'h', 'value': 'hours'},
            {'name': 'hrs', 'value': 'hours'},
            # {'name': '', 'value': ''},
        ]

        for pattern in units:
            if pattern['name'] in string:
                return pattern['value']

        return string

    @staticmethod
    def parse_seconds_from_time(measure, unit):
        measure = float(measure)
        result = 0

        if unit == 'days':
            result = measure * 24 * 60 * 60
        elif unit == 'hours':
            result = measure * 60 * 60
        elif unit == 'minuetes':
            result = measure * 60
        elif unit == 'seconds':
            result = measure

        return str(result)
