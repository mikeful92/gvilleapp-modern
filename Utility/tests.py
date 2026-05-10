from django.test import TestCase

from Utility.views import normalize_address


class NormalizeAddressTests(TestCase):
    def test_strips_city_and_state(self):
        self.assertEqual(
            normalize_address("758 NW 18TH TERRACE, GAINESVILLE, FL"),
            "758 NW 18TH TER",
        )

    def test_expands_directionals(self):
        self.assertEqual(
            normalize_address("100 Northwest 6th Street"),
            "100 NW 6TH ST",
        )

    def test_collapses_whitespace(self):
        self.assertEqual(
            normalize_address("   100   SE   10TH   AVENUE   "),
            "100 SE 10TH AVE",
        )


class HomeViewTests(TestCase):
    def test_home_returns_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gainesville Utility")
