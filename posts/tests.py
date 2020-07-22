from django.test import TestCase
from django.test import Client
from posts.models import Post, Group, User
from django.urls import reverse


class TestPosts(TestCase):
    def setUp(self):
        self.group1 = Group.objects.create(
            title='testGroup1',
            slug='test_slug1',
            description='описание группы1'
        )
        self.client_on = Client()
        self.client_off = Client()
        self.user = User.objects.create(
            username='test_user', email='q@q.com')
        self.user.set_password('123')
        self.user.save()
        self.client_on.force_login(self.user)
        self.clients = (self.client_on, self.client_off,)

    def _get_url(self):
        return {
            'index':
                reverse('index'),
            'profile':
                reverse('profile', kwargs={'username': self.user.username}),
            'post':
                reverse('post',
                        kwargs={
                            'username': self.post.author,
                            'post_id': self.post.id
                        })
        }

    def test_new_post_user_on(self):
        """
        Проверка, что зарегистрированный пользователь может создать пост
        """
        response = self.client_on.post(
            reverse('new_post'),
            data={
                'text': 'test text',
                'group': self.group1.id
            }
        )
        self.assertRedirects(response,
            expected_url=reverse('index'),
            status_code=302,
            target_status_code=200,
            msg_prefix='',
            fetch_redirect_response=True
        )
        self.assertEqual(Post.objects.count(), 1)
        self.assertTrue(Post.objects.filter(
            text='test text',
            group=self.group1.id),
            msg="Зарегистрированный пользователь может создать пост")

    def test_new_post_user_off(self):
        """
        Проверка, что незарегистрированный пользователь
        редиректится на страницу входа
        """
        response = self.client_off.get(reverse('new_post'))
        reverse1 = reverse('login')
        reverse2 = reverse('new_post')
        self.assertRedirects(response,
            expected_url=f'{reverse1}?next={reverse2}',
            status_code=302,
            target_status_code=200,
            msg_prefix='',
            fetch_redirect_response=True
        )

    def test_view_new_post(self):
        """
        Проверка отображение нового поста
        """
        self._create_new_post('test text 1')
        urls = self._get_url()
        for client in self.clients:
            for url in urls.values():
                response = self.client.get(url)
                self.assertContains(
                    response,
                    self.post.text,
                    count=None,
                    status_code=200,
                    msg_prefix='',
                    html=False)

    def _create_new_post(self, text):
        self.post = Post.objects.create(
            text=text,
            group=self.group1,
            author=self.user
        )

    def _edit_post(self, text):
        self.response = self.client_on.post(
            reverse('post_edit',  kwargs={
                    'username': self.user.username, 'post_id': self.post.id}),
            data={'username': self.user.username,
                  'post_id': self.post.id,
                  })

    def test_edit_post_user_on(self):
        """
        Проверка редактирования поста
        зарегистрированным пользователем
        """
        self._create_new_post('test text 2')
        self._edit_post(text='Новый текст зарегистрированного пользователя')
        self.assertEqual(self.response.status_code,
            200, msg="Проверка редактирования поста"
        )

    def test_edit_post_view(self):
        """
        Проверка отображения отредактированного поста
        зарегистрированным пользователем
        """
        self._create_new_post('test text 3')
        self._edit_post(text='Новый текст')
        self.post = Post.objects.select_related('group').first()
        check_fields = (self.post.text, self.post.author.username)
        urls = self._get_url()
        for test_url in urls.values():
            response = self.client.get(test_url)
            for check_field in check_fields:
                self.assertContains(
                    response,
                    check_field,
                    count=None,
                    status_code=200,
                    msg_prefix='',
                    html=False
                )
