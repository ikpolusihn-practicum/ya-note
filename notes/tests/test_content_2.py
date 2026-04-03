from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.authorised_user = User.objects.create(username='authorised_user')
        cls.note_author = User.objects.create(username='note_author')
        cls.login_url = reverse('users:login')

        cls.note = Note.objects.create(
            title='title_note_1_user_1',
            text='text_note_1_user_1',
            slug='note_1_user_1',
            author=cls.note_author,
        )

    def test_note_in_list(self):
        test_sets = (
            ('authorised_user', self.authorised_user,),
            ('note_author', self.note_author,),
        )

        for scenario, user in test_sets:
            self.client.force_login(user)
            url = reverse('notes:list')
            response = self.client.get(url)
            object_list = response.context['object_list']

            with self.subTest(name=scenario):
                if scenario == 'note_author':
                    self.assertIn(self.note, object_list)
                elif scenario == 'authorised_user':
                    self.assertNotIn(self.note, object_list)

    def test_form_in_page(self):
        test_sets = (
            ('add_note', 'notes:add', None),
            ('edit_note', 'notes:edit', (self.note.slug, )),
        )

        for scenario, url, url_args in test_sets:
            self.client.force_login(self.note_author)
            url = reverse(url, args=url_args)
            response = self.client.get(url)
            self.assertIsInstance(response.context['form'], NoteForm)
