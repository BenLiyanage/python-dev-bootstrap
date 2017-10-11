import os
import scrapy


class Drugs(scrapy.Spider):
    name = "DrugScraper"
    starts_urls = [
        # 'https://en.wikipedia.org/wiki/Category:Drugs_by_target_organ_system'
        'https://en.wikipedia.org/wiki/Omeprazole'
    ]
    def start_requests(self):
        try:
            os.remove('stats.csv')
        except FileNotFoundError:
            pass

        urls = [
            # 'https://en.wikipedia.org/wiki/Category:Drugs_by_target_organ_system'
            'https://en.wikipedia.org/wiki/Omeprazole'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if 'Category' in response.url:
            # Need to return the yielded list of URLs, if it exists.
            return self.parse_category(response)
        else:
            self.parse_drug(response)
        # page = response.url.split("/")[-2]
        # filename = 'quotes-%s.html' % page


        # next_page = response.css('li.next a::attr(href)').extract_first()
        # if next_page is not None:
        # next_page = response.urljoin(next_page)
        # yield scrapy.Request(next_page, callback=self.parse)

        # for a in response.css('li.next a'):
        #     yield response.follow(a, callback=self.parse)

        import pdb

        pdb.set_trace()

    def parse_category(self, response):
        self.log(response.css('.mw-category a').extract())
        for a in response.css('.mw-category a'):
            yield response.follow(a, callback=self.parse)

    def parse_drug(self, response):

        stats = [None] * 3
        HALF_LIFE = 0
        HALF_LIFE_RAW = 3
        DRUG_BANK = 1
        DRUG_BANK_RAW = 4
        DRUG_CLASS = 2
        DRUG_CLASS_RAW = 5

        # Loop over the rows of the info box
        for item in (response.css('.infobox tr')):
            link_title = item.css('th a::attr(title)').extract_first()
            value = item.css('td')
            print(link_title)
            print(item.css('th').extract_first())

            if link_title == 'Biological half-life':
                stats[HALF_LIFE] = value.css('td::text').extract()
                stats[HALF_LIFE_RAW] = value
            elif link_title == 'DrugBank':
                stats[DRUG_BANK] = value.css('a::text').extract()
                stats[DRUG_BANK_RAW] = value
            elif link_title == 'Drug class':
                stats[DRUG_CLASS] = value.css('a::text')
                stats[DRUG_CLASS_RAW] = value
                # filename = 'by_system.html'
                # with open(filename, 'wb') as f:
                #     f.write(response.body)
                # self.log('Saved file %s' % filename)

        import pdb
        pdb.set_trace()
