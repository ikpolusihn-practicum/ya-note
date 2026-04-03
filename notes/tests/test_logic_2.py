import pytils

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.core.exceptions import ValidationError

from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.authorised_user = User.objects.create(username='authorised_user')
        cls.note_author = User.objects.create(username='note_author')
        cls.login_url = reverse('users:login')

        cls.new_note_1_data = {
            'title': 'new_note_title',
            'text': 'new_note_text',
            'slug': 'new_note_slug',
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
                    self.assertEqual(notes_count, 0)

                    response = self.client.post(url, data=self.new_note_1_data)
                    self.assertRedirects(response, reverse('notes:success'))

                    notes_count = Note.objects.count()
                    self.assertEqual(notes_count, 1)

                    created_note = Note.objects.get()
                    self.assertEqual(
                        (
                            created_note['title'],
                            created_note['text'],
                            created_note['slug']
                        ),
                        (
                            self.new_note_1_data['title'],
                            self.new_note_1_data['text'],
                            self.new_note_1_data['slug'],
                        )
                    )

                elif scenario == 'unauthorized_user':

                    notes_count = Note.objects.count()
                    self.assertEqual(notes_count, 0)

                    self.client.post(url, data=self.new_note_1_data)

                    response = self.client.post(url, data=self.new_note_1_data)
                    redirect_url = f'{self.login_url}?next={url}'
                    self.assertRedirects(response, redirect_url)

                    notes_count = Note.objects.count()
                    self.assertEqual(notes_count, 0)

    def test_note_creation_with_the_same_slug(self):
        url = reverse('notes:add')
        self.client.force_login(self.note_author)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

        self.client.post(url, data=self.new_note_1_data)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

        self.client.post(url, data=self.new_note_1_data)
        self.assertRaises(ValidationError)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_empty_slug_creation(self):
        url = reverse('notes:add')
        self.client.force_login(self.note_author)

        self.new_note_1_data.pop('slug')
        response = self.client.post(url, data=self.new_note_1_data)
        self.assertRedirects(response, reverse('notes:success'))

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

        created_note = Note.objects.get()
        expected_slug = pytils.translit.slugify(self.new_note_1_data['title'])
        self.assertEqual(created_note.slug, expected_slug)



