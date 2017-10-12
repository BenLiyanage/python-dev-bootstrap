import json
import os
import scrapy
from bs4 import BeautifulSoup


class Drugs(scrapy.Spider):
    name = "DrugScraper"
    filemask = "./data/{}/{}"

    # Constants for file position
    HALF_LIFE = 0
    HALF_LIFE_RAW = 3
    DRUG_BANK = 1
    DRUG_BANK_RAW = 4
    DRUG_CLASS = 2
    DRUG_CLASS_RAW = 5

    custom_settings = {
        'DEPTH_LIMIT': 2,
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
                    stats[self.HALF_LIFE_RAW] = raw_value
                elif link_title == 'DrugBank':
                    stats[self.DRUG_BANK] = value
                    stats[self.DRUG_BANK_RAW] = raw_value
                elif link_title == 'Drug class':
                    stats[self.DRUG_CLASS] = value
                    stats[self.DRUG_CLASS_RAW] = raw_value

        # Using this as a fingerprint for this being a page about a drug...
        # Probably not the best fingerprint, but it works ok given the small scope.
        if len(infobox.keys()):
            self.save_string(drug_name, json.dumps(data), 'data.json')
            with open('./stats.csv', 'a') as stats_file:
                stats_file.write('"{}", "{}"\n'.format('", "'.join(stats[0:3]), response.url))

    def save_string(self, drug_name, string, filename):
        drug_folder = './data/{}'.format(drug_name)
        drug_filename = '{}/{}'.format(drug_folder, filename)
        os.makedirs(drug_folder, exist_ok=True)
        with open(drug_filename, 'w') as drug_file:
            drug_file.write(string)
