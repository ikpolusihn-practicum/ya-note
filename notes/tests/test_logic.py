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

    def update_note_by_author(self):
        new_title = 'new_title'
        new_text = 'new_text'

        self.auth_client.force_login(self.user_1)
        url = reverse('notes:edit', args=(self.notes.slug,))
        current_response = self.auth_client.get(url)

        current_form = current_response.context['form']
        current_slug = current_form.initial.get('slug')

        new_data = {
            'title': new_title,
            'text': new_text,
            'slug': current_slug,
        }
        response = self.auth_client.post('notes:edit', new_data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, 'notes:success')

        updated_response = self.auth_client.get(url)
        updated_form = updated_response.context['form']
        updated_title = updated_form.initial.get('title')
        updated_text = updated_form.initial.get('text')
        updated_slug = updated_form.initial.get('slug')

        self.assertEqual(
            {updated_title, updated_text, updated_slug},
            {new_title, new_text, current_slug},
        )

    def update_note_by_other_user(self):
        self.auth_client.force_login(self.user_2)
        url = reverse('notes:edit', args=(self.notes.slug,))
        response = self.auth_client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

        new_data = {
            'title': 'new_title',
            'text': 'new_text',
            'slug': 'new_slug',
        }

        response = self.auth_client.post(
            'notes:edit',
            new_data,
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def update_note_by_unauthorized_user(self):
        url = reverse('notes:edit', args=(self.notes.slug,))
        response = self.auth_client.get(url)

        redirect_url = f'{self.login_url}?next={url}'
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, redirect_url)

        new_data = {
            'title': 'new_title',
            'text': 'new_text',
            'slug': 'new_slug',
        }

        response = self.auth_client.post(
            'notes:edit',
            new_data,
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, redirect_url)
