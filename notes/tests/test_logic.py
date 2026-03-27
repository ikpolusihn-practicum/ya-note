from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note

User = get_user_model()

class TestNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_1 = User.objects.create(username='user_1')
        cls.user_2 = User.objects.create(username='user_2')
        cls.auth_client = Client()

        cls.notes = Note.objects.create(
            title='title_note_1_user_1',
            text='text_note_1_user_1',
            slug='note_1_user_1',
            author=cls.user_1,
        )

        cls.login_url = reverse('users:login')

    def test_display_note_by_author(self):
        self.auth_client.force_login(self.user_1)
        url = reverse('notes:detail', args=(self.notes.slug,))
        response = self.auth_client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_display_note_by_other_user(self):
        self.auth_client.force_login(self.user_2)
        url = reverse('notes:detail', args=(self.notes.slug,))
        response = self.auth_client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_display_note_by_unauthorized_user(self):
        url = reverse('notes:detail', args=(self.notes.slug,))
        response = self.auth_client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        redirect_url = f'{self.login_url}?next={url}'
        self.assertRedirects(response, redirect_url)

    def test_delete_note_by_author(self):
        self.auth_client.force_login(self.user_1)

        notes_count = Note.objects.filter(author=self.user_1).count()
        self.assertEqual(notes_count, 1)

        url = reverse('notes:delete', args=(self.notes.slug,))
        response = self.auth_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        redirect_url = reverse('notes:success')
        self.assertRedirects(response, redirect_url)

        notes_count = Note.objects.filter(author=self.user_1).count()
        self.assertEqual(notes_count, 0)

    def test_delete_note_by_other_user(self):
        self.auth_client.force_login(self.user_2)

        notes_count = Note.objects.filter(author=self.user_1).count()
        self.assertEqual(notes_count, 1)

        url = reverse('notes:delete', args=(self.notes.slug,))
        response = self.auth_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        notes_count = Note.objects.filter(author=self.user_1).count()
        self.assertEqual(notes_count, 1)

    def test_delete_note_by_unauthorised_user(self):
        notes_count = Note.objects.filter(author=self.user_1).count()
        self.assertEqual(notes_count, 1)

        url = reverse('notes:delete', args=(self.notes.slug,))
        response = self.auth_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        redirect_url = f'{self.login_url}?next={url}'
        self.assertRedirects(response, redirect_url)

        notes_count = Note.objects.filter(author=self.user_1).count()
        self.assertEqual(notes_count, 1)
