from datetime import datetime

from django import forms
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_static_pages_urls(self):
        url_names = (
            reverse("about:author"),
            reverse("about:tech"),
        )
        for reverse_name in url_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name, follow=True)
                self.assertEqual(response.status_code, 200)


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём запись в БД для проверки доступности адреса group/<slug>/
        cls.author = User.objects.create(username="TestUser")
        # Создаём записи в БД для проверки подписки
        cls.follower = User.objects.create(username="Follower")
        cls.following = User.objects.create(username="Following")
        # Создаем неавторизованный клиент
        cls.guest_client = Client()
        # Создаем авторизованных клиентов
        cls.authorized_client = Client()
        cls.authorized_follower = Client()
        cls.authorized_following = Client()
        # Авторизуем пользователей
        cls.authorized_client.force_login(cls.author)
        cls.authorized_follower.force_login(cls.follower)
        cls.authorized_following.force_login(cls.following)
        cls.image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='image.gif',
            content=cls.image,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title="Test title",
            description="Test description",
            slug="Test_Slug",
        )
        cls.group_empty = Group.objects.create(
            title="Second group",
            description="Group for test 'new post'",
            slug="Second_group",
        )
        # Создаём тестовый пост в группе
        cls.post = Post.objects.create(
            text="Test!"*6,
            pub_date=datetime.now,
            author=cls.author,
            group=cls.group,
            image=cls.uploaded,
        )
        cls.comment = Comment.objects.create(
            author=cls.author,
            post=cls.post,
            text="Test comment"
        )

    # Проверяем используемые шаблоны
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            "index.html": reverse("index"),
            "group.html": reverse("group", kwargs={"slug": self.group.slug}),
            "new_post.html": reverse("new_post"),
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_group_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse("group", kwargs={
            "slug": self.group.slug
        }))
        # Тестируем отдельно поля шаблона группы
        group_title = response.context.get("group").title
        group_slug = response.context.get("group").slug
        group_description = response.context.get("group").description
        self.assertEqual(group_title, PostsPagesTests.group.title)
        self.assertEqual(group_slug, PostsPagesTests.group.slug)
        self.assertEqual(group_description, PostsPagesTests.group.description)
        # То же самое, но короче в 2 раза
        actual_group = response.context.get("group")
        expected_group = PostsPagesTests.group
        self.assertEqual(actual_group, expected_group)

    def test_new_post_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("new_post"))
        # Список ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
            "image": forms.fields.ImageField,
        }
        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("index"))
        expected = Post.objects.all()[:10]
        actual_response = response.context.get("page").object_list
        self.assertListEqual(list(actual_response), list(expected))

    def test_index_cache(self):
        """Кэш для Posts на странице index функционирует корректно"""
        response_with_1_post = self.client.get(reverse("index") + "?page=1")
        Post.objects.create(
                text="Second Post",
                pub_date=datetime.now(),
                author=PostsPagesTests.author,
                group=PostsPagesTests.group,
                image=PostsPagesTests.uploaded,
            )
        response_with_2_posts = self.client.get(reverse("index") + "?page=1")
        self.assertHTMLEqual(
            str(response_with_1_post.content),
            str(response_with_2_posts.content)
        )
        cache.clear()
        response_with_2_posts = self.client.get(reverse("index") + "?page=1")
        self.assertHTMLNotEqual(
            str(response_with_1_post.content),
            str(response_with_2_posts.content)
        )

    def test_newpost_created_only_one_group(self):
        """Новый пост создаётся в конкретной группе и нигде больше."""
        expected = PostsPagesTests.post
        response_actual_group = self.authorized_client.get(
            reverse("group", kwargs={"slug": "Test_Slug"})
        )
        response_epty_group = self.authorized_client.get(
            reverse("group", kwargs={"slug": "Second_group"})
        )
        response_index = self.authorized_client.get(reverse("index"))
        # В пустой группе так и осталось пусто
        self.assertQuerysetEqual(response_epty_group.context["page"], [])
        # В группе поста созан пост, в котором указана эта группа
        self.assertEqual(response_actual_group.context["page"][0], expected)
        # Созданный пост отображается на главной странице также
        self.assertEqual(response_index.context["page"][0], expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("post_edit", args=[
            self.post.author.username, self.post.id
        ]))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
            "image": forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_view_show_correct_context(self):
        """Шаблон одного поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("post", args=[
            self.post.author.username, self.post.id
        ]))
        actual_response = response.context.get("user").posts.all()[0]
        expected = PostsPagesTests.post
        self.assertEqual(actual_response, expected)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("profile", args=[
            PostsPagesTests.post.author.username
        ]))
        expected = PostsPagesTests.post
        actual_response = response.context.get("user").posts.all()[0]
        self.assertEqual(actual_response, expected)

    def test_post_comment_show_correct_context(self):
        """Шаблон Comment сформирован с правильным контекстом."""
        expected_url = reverse(
            "add_comment", kwargs={
                "username": PostsPagesTests.author.username,
                "post_id": PostsPagesTests.post.id,
            }
        )
        response = self.authorized_client.get(expected_url)
        form_fields = {"text": forms.fields.CharField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_user_follow_and_unfollow(self):
        """Подписаться можно только на одного автора. Авторизованный
        пользователь подписывается на других пользователей и отписывается"""
        expected_url = reverse(
            "profile_follow", kwargs={"username": self.following}
        )
        self.authorized_follower.get(expected_url)
        expected_follows = Follow.objects.filter(author=self.following)
        self.assertEqual(expected_follows.count(), 1)
        # Проверяем ленту подписчиков автора, кто не подписан на following
        expected_follows = Follow.objects.filter(author=self.author)
        self.assertEqual(expected_follows.count(), 0)
        # Отписываем фоловера
        Follow.objects.get(user=self.follower, author=self.following).delete()
        expected_follows = Follow.objects.filter(author=self.following)
        self.assertEqual(expected_follows.count(), 0)
