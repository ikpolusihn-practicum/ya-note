from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='some_user')
        cls.auth_client = Client()
        cls.login_url = reverse('users:login')

    def test_authorised_user(self):

        test_sets = (
            {
                'url_name': 'notes:home',
                'exp_result': HTTPStatus.OK,
            },
            {
                'url_name': 'notes:list',
                'exp_result': HTTPStatus.OK,
            },
            {
                'url_name': 'notes:add',
                'exp_result': HTTPStatus.OK,
            },
            {
                'url_name': 'users:logout',
                'exp_result': HTTPStatus.METHOD_NOT_ALLOWED,
            },
        )

        for test_set in test_sets:
            url = test_set['url_name']
            exp_result = test_set['exp_result']

            with self.subTest(name=url):
                self.auth_client.force_login(self.user)
                url = reverse(url)
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, exp_result)

    def test_unauthorized_user(self):
        test_sets = (
            {
                'url_name': 'notes:home',
                'exp_result': HTTPStatus.OK,
            },
            {
                'url_name': 'notes:list',
                'exp_result': HTTPStatus.FOUND,
            },
            {
                'url_name': 'notes:add',
                'exp_result': HTTPStatus.FOUND,
            },
            {
                'url_name': 'users:login',
                'exp_result': HTTPStatus.OK,
            },
            {
                'url_name': 'users:signup',
                'exp_result': HTTPStatus.OK,
            },
            {
                'url_name': 'users:logout',
                'exp_result': HTTPStatus.METHOD_NOT_ALLOWED,
            },
        )

        for test_set in test_sets:
            url = test_set['url_name']
            exp_result = test_set['exp_result']

            with self.subTest(name=url):
                url = reverse(url)
                response = self.client.get(url)
                self.assertEqual(response.status_code, exp_result)

    def test_unauthorized_user_redirect(self):

        test_sets = (
            {
                'url_name': 'notes:list',
            },
            {
                'url_name': 'notes:add',
            },
        )

        for test_set in test_sets:
            url = test_set['url_name']

            with self.subTest(name=url):
                url = reverse(url)
                response = self.client.get(url)
                redirect_url = f'{self.login_url}?next={url}'
                self.assertRedirects(response, redirect_url)
