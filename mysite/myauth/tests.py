from django.test import TestCase
from django.urls import reverse
import json

# Create your tests here.
class GetCookieViewTestCase(TestCase):
    def test_get_cookie_view(self):
        response = self.client.get(reverse('myauth:cookie_get'))
        self.assertContains(response, "Cookie value")

class FooBarViewTest(TestCase):
    def test_foo_bar_view(self):
        response = self.client.get(reverse('myauth:foo-bar'))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.headers['content-type'], 'application/json')

        exepted_data = {'foo': 'bar', 'bar': 'baz'}
        # received_data = json.loads(response.content)
        # self.assertEquals(received_data, exepted_data)
        self.assertJSONEqual(response.content, exepted_data)