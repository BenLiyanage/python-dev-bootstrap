from unittest import TestCase

from drugscraper.drugscraper.spiders.spider import Drugs


class SpiderTest(TestCase):
    def test_parse_halflife(self):
        h_min, h_max = Drugs.parse_halflife('1.3 to 1.7 hours')
        self.assertEqual(h_min, '4680.0')
        self.assertEqual(h_max, '6120.0')
