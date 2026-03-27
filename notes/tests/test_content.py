from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note

User = get_user_model()

class TestNotesList(TestCase):

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


    def test_notes_display_user_with_notes(self):
        self.auth_client.force_login(self.user_1)

        response = self.auth_client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        notes_count = object_list.count()

        self.assertEqual(notes_count, 1)

    def test_note_creation_user_with_notes(self):
        data = {
            'title': 'title_note_2_user_1',
            'text': 'text_note_2_user_1',
            'slug': 'note_2_user_1',
        }

        self.auth_client.force_login(self.user_1)
        url = reverse('notes:add')
        self.auth_client.post(url, data)

        response = self.auth_client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        notes_count = object_list.count()

        self.assertEqual(notes_count, 2)

    def test_notes_display_user_without_notes(self):
        self.auth_client.force_login(self.user_2)

        response = self.auth_client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        notes_count = object_list.count()

        self.assertEqual(notes_count, 0)

    def test_note_creation_user_without_notes(self):
        data = {
            'title': 'title_note_2_user_1',
            'text': 'text_note_2_user_1',
            'slug': 'note_2_user_1',
        }

        self.auth_client.force_login(self.user_1)
        url = reverse('notes:add')
        self.auth_client.post(url, data)

        self.auth_client.force_login(self.user_2)
        response = self.auth_client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        notes_count = object_list.count()

        self.assertEqual(notes_count, 0)

    def test_form_exists(self):
        ...