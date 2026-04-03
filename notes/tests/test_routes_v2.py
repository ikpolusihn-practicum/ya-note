import unittest
from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.authorised_user = User.objects.create(username='authorised_user')
        cls.note_author = User.objects.create(username='note_author')
        cls.login_url = reverse('users:login')

        cls.notes = Note.objects.create(
            title='title_note_1_user_1',
            text='text_note_1_user_1',
            slug='note_1_user_1',
            author=cls.note_author,
        )


    def test_availability_unauthorised_user(self):
        test_sets = (
            {
                'url_name': 'notes:home',
                'exp_result': HTTPStatus.OK,
                'arguments': None,
            },
            {
                'url_name': 'notes:list',
                'exp_result': HTTPStatus.FOUND,
                'arguments': None,
            },
            {
                'url_name': 'notes:add',
                'exp_result': HTTPStatus.FOUND,
                'arguments': None,
            },
            {
                'url_name': 'notes:success',
                'exp_result': HTTPStatus.FOUND,
                'arguments': None,
            },
            {
                'url_name': 'users:login',
                'exp_result': HTTPStatus.OK,
                'arguments': None,
            },
            {
                'url_name': 'users:signup',
                'exp_result': HTTPStatus.OK,
                'arguments': None,
            },
            {
                'url_name': 'notes:detail',
                'exp_result': HTTPStatus.FOUND,
                'arguments': (self.notes.pk, ),
            },
            {
                'url_name': 'notes:edit',
                'exp_result': HTTPStatus.FOUND,
                'arguments': (self.notes.pk,),
            },
            {
                'url_name': 'notes:delete',
                'exp_result': HTTPStatus.FOUND,
                'arguments': (self.notes.pk,),
            },
        )

        for test_set in test_sets:
            url = test_set['url_name']
            exp_result = test_set['exp_result']
            arguments = test_set['arguments']

            with self.subTest(name=url):
                url = reverse(url, args=arguments,)
                response = self.client.get(url)
                self.assertEqual(response.status_code, exp_result)

                if url in (
                    'notes:list', 'notes:add', 'notes:success',
                    'notes:detail', 'notes:delete', 'notes:edit',
                ):
                    redirect_url = f'{self.login_url}?next={url}'
                    self.assertRedirects(response, redirect_url)
