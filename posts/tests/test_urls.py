from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class ErrorURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_error_pages_urls(self):
        url_names = {
            "misc/500.html": reverse("error500"),
            "misc/404.html": reverse("error404"),
        }
        for template, reverse_name in url_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name, follow=True)
                self.assertTemplateUsed(response, template)

    def test_error_pages_staus_code(self):
        url_names = {
            reverse("error500"): 500,
            reverse("error404"): 404,
        }
        for reverse_name, status in url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name, follow=True)
                self.assertEqual(response.status_code, status)


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Test title",
            description="Test description",
            slug="Test_Slug",
        )
        cls.user = User.objects.create(username="TestUser")
        cls.post = Post.objects.create(
            text="Test!"*6,
            author=cls.user,
            group=cls.group,
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_url_allowed_to_anonymous(self):
        """Доступные страницы для неавторизованных пользователей."""
        url_names = (
            reverse("index"),
            reverse("group", kwargs={"slug": self.group.slug}),
            reverse("profile", args=[PostsURLTests.post.author.username]),
            reverse("post", args=[
                PostsURLTests.post.author.username, PostsURLTests.post.id
            ]),
        )
        for reverse_name in url_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name, follow=True)
                self.assertEqual(response.status_code, 200)

    def test_url_redirect_anonymous_on_auth_login(self):
        """Перенаправление неавторизованных пользователей на страницу логина.
        """
        post = PostsURLTests.post
        response = self.guest_client.get(reverse(
            "post_edit", args=[post.author.username, post.id]
        ))
        url_names = (
            reverse("new_post"),
            reverse("profile_follow", args=[
                PostsURLTests.post.author.username
            ]),
            reverse("add_comment", kwargs={
                "username": PostsURLTests.post.author.username,
                "post_id": PostsURLTests.post.id,
            })
        )
        for reverse_name in url_names:
            with self.subTest(reverse_name=reverse_name):
                url_redirect = reverse("login") + "?next=" + reverse_name
                response = self.guest_client.get(reverse_name, follow=True)
                self.assertRedirects(response, url_redirect)

    def test_url_allowed_to_authorized_client(self):
        """Страницы доступны для авторизованных пользователей."""
        url_names = (
            reverse("index"),
            reverse("group", kwargs={"slug": self.group.slug}),
            reverse("new_post"),
        )
        for reverse_name in url_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(
                    reverse_name, follow=True
                )
                self.assertEqual(response.status_code, 200)

    def test_url_post_edit_redirect(self):
        """Перенаправление на страницу просмотра поста всех пользователей,
        кто не является автором поста при попытке редактировать пост."""
        post = PostsURLTests.post
        response = self.guest_client.get(reverse(
            "post_edit", args=[post.author.username, post.id]
        ))
        url_names = (
            reverse("post_edit", args=[post.author.username, post.id]),
        )
        for reverse_name in url_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name, follow=True)
                self.assertEqual(response.status_code, 200)
