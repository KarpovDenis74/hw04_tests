from django.test import TestCase
from django.test import Client
from posts.models import Post, Group
from django.contrib.auth import get_user_model
from django.urls import reverse
# Create your tests here.

User = get_user_model()


class TestClientMixin:
    def setUp(self):
        self.client = Client()

    def create_user(self):
        self.user = User.objects.create(
            username='test_user', email='q@q.com')
        self.user.set_password('123')
        self.user.save()

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

    def login_user(self):
        self.client.login(username=self.user.username, password='123')

    def _create_new_post(self):
        self.create_user()
        self.login_user()
        group = Group.objects.create(
            title='testGroup',
            slug='test_slug',
            description='описание группы'
        )
        self.group_id = group.id
        self.client.post(
            '/new/',
            data={
                'text': 'test text',
                'group': self.group_id
            }
        )
        posts = Post.objects.filter(text='test text', group=self.group_id)[:1]
        for post in posts:
            self.post = post
            break

        def tearDoun(self):
            print('The End')


class TestProlil(TestCase, TestClientMixin):
    def test_profile(self):
        self.create_user()
        response = self.client.get(
            reverse('profile', kwargs={'username': self.user.username}))
        self.assertEqual(
            response.status_code, 200,
            msg="Проверка, что страница profile пользователя ")


class TestCreatNewPost(TestCase, TestClientMixin):
    def test_new_post_user_on(self):
        """
        Проверка, что зарегистрированный пользователь может создать пост
        """
        self._create_new_post()
        self.assertTrue(Post.objects.filter(
            text='test text',
            group=self.group_id),
            msg="Зарегистрированный пользователь может создать пост")

        def test_new_post_user_off(self):
        """
        Проверка, что незарегистрированный пользователь
        редиректится на страницу входа
        """
        self.client.logout()
        response = self.client.get(reverse('new_post'))
        self.assertRedirects(response,
            expected_url='/auth/login/?next=%2Fnew%2F',
            status_code=302,
            target_status_code=200,
            msg_prefix='',
            fetch_redirect_response=True)

    def test_view_new_post(self):
        """
        Проверка отображение нового поста
        """
        self._create_new_post()
        urls = self._get_url()
        for test_url in urls.values():
            response = self.client.get(test_url)
            self.assertContains(
                response,
                self.post.text,
                count=None,
                status_code=200,
                msg_prefix='',
                html=False)


class TestEditPost(TestClientMixin, TestCase):
    def _edit_post(self):
        self.response = self.client.post(
            reverse('post_edit',  kwargs={
                    'username': self.user.username, 'post_id': self.post.id}),
            data={'username': self.user.username,
                  'post_id': self.post.id})

    def test_edit_post_user_on(self):
        """
        Проверка редактирования поста
        зарегистрированным пользователем
        """
        self._create_new_post()
        self._edit_post()
        self.assertEqual(self.response.status_code,
            200, msg="Проверка редактирования поста")

    def test_edit_post_view(self):
        """
        Проверка отображения отредактированного поста
        зарегистрированным пользователем
        """
        self._create_new_post()
        self._edit_post()
        urls = self._get_url()
        for test_url in urls.values():
            response = self.client.get(test_url)
            self.assertContains(
                response,
                self.post.text,
                count=None,
                status_code=200,
                msg_prefix='',
                html=False)
