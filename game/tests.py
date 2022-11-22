from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from .views import HomePageView


# Create your tests here.
class GameTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_homepage(self):
        request = self.factory.get('/')
        response = HomePageView.as_view()(request)
        self.assertEqual(response.status_code, 200)
