import pytils
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, Client
from django.core.exceptions import ValidationError

from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.authorised_user = User.objects.create(username='authorised_user')
        cls.note_author = User.objects.create(username='note_author')
        cls.login_url = reverse('users:login')

        cls.note = Note.objects.create(
            title='title_note_1',
            text='text_note_1',
            slug='note_1',
            author=cls.note_author,
        )

        cls.new_note_2_data = {
            'title': 'title_note_2',
            'text': 'text_note_2',
            'slug': 'note_2',
        }

    def test_note_creation(self):

        test_sets = (
            ('authorized_user', ),
            ('unauthorized_user', )
        )

        for scenario in test_sets:

            url = reverse('notes:add')

            with self.subTest(name=scenario):
                if scenario == 'authorized_user':
                    self.client.force_login(self.note_author)

                    notes_count = Note.objects.count()
                    self.assertEqual(notes_count, 1)

                    response = self.client.post(url, data=self.new_note_2_data)
                    self.assertRedirects(response, reverse('notes:success'))

                    notes_count = Note.objects.count()
                    self.assertEqual(notes_count, 2)

                    created_note = Note.objects.get()
                    self.assertEqual(
                        (
                            created_note['title'],
                            created_note['text'],
                            created_note['slug']
                        ),
                        (
                            self.new_note_2_data['title'],
                            self.new_note_2_data['text'],
                            self.new_note_2_data['slug'],
                        )
                    )

                elif scenario == 'unauthorized_user':

                    notes_count = Note.objects.count()
                    self.assertEqual(notes_count, 1)

                    self.client.post(url, data=self.new_note_2_data)

                    response = self.client.post(url, data=self.new_note_2_data)
                    redirect_url = f'{self.login_url}?next={url}'
                    self.assertRedirects(response, redirect_url)

                    notes_count = Note.objects.count()
                    self.assertEqual(notes_count, 1)

    def test_note_creation_with_the_same_slug(self):
        url = reverse('notes:add')
        self.client.force_login(self.note_author)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

        self.client.post(
            url,
            data={
                'title': self.note.title,
                'text': self.note.text,
                'slug': self.note.slug,
            }
        )
        self.assertRaises(ValidationError)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_empty_slug_creation(self):
        url = reverse('notes:add')
        self.client.force_login(self.note_author)

        self.new_note_2_data.pop('slug')
        response = self.client.post(url, data=self.new_note_2_data)
        self.assertRedirects(response, reverse('notes:success'))

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)

        created_note = Note.objects.get(id=2)
        expected_slug = pytils.translit.slugify(self.new_note_2_data['title'])
        self.assertEqual(created_note.slug, expected_slug)

    def test_other_user_cant_delete_note(self):
        self.client.force_login(self.authorised_user)
        url = reverse('notes:delete', args=(self.note.slug, ))
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_other_user_cant_edit_note(self):
        self.client.force_login(self.authorised_user)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(
            url,
            data=self.new_note_2_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(
            (self.note.title, self.note.text, self.note.slug),
            (note_from_db.title, note_from_db.text, note_from_db.slug)
        )

    def test_author_can_delete_note(self):
        self.client.force_login(self.note_author)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('notes:success'))

    def test_author_can_edit_note(self):
        self.client.force_login(self.note_author)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(
            url,
            data=self.new_note_2_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('notes:success'))

        self.note.refresh_from_db()
        self.assertEqual(
            (self.note.title, self.note.text, self.note.slug),
            (
                self.new_note_2_data['title'],
                self.new_note_2_data['text'],
                self.new_note_2_data['slug']
            )
        )
