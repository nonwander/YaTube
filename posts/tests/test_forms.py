from datetime import datetime

from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username="TestUser")
        cls.group = Group.objects.create(
            title="Test title",
            description="Test description",
            slug="Test_Slug",
        )
        # Создаём тестовый пост в группе
        cls.post = Post.objects.create(
            text="Test Post",
            pub_date=datetime.now,
            author=PostCreateFormTests.author,
            group=PostCreateFormTests.group,
        )
        cls.form = PostForm()
        cls.comment = Comment.objects.create(
            author=cls.author,
            post=cls.post,
            text="Test Comment"
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.author)

    def test_create_new_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            "group": self.group.id,
            "text": "New post",
        }
        self.authorized_client.post(
            reverse("new_post"),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count+1)
        self.assertTrue(Post.objects.filter(
            text=form_data["text"],
            group=form_data["group"],
            author=self.author.id
        ).exists())

    def test_edit_post(self):
        """Запись при редактировании успешно меняется"""
        expected_text = PostCreateFormTests.post.text
        # проверим текстовое поле до отправления формы
        self.assertTrue(Post.objects.filter(text=expected_text).exists())
        form_data = {
            "text": "New text for test",
            "group": self.group.id,
        }
        expected_url = reverse("post_edit", kwargs={
            "username": self.post.author.username,
            "post_id": self.post.id
        })
        response = self.authorized_client.post(
            expected_url,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            "post", args=[self.post.author.username, self.post.id]
        ))
        self.post.refresh_from_db()
        expected_text = form_data["text"]
        # проверим текстовое поле после отправления формы
        self.assertTrue(Post.objects.filter(text=expected_text).exists())
        # изменим текстовое поле без отправления формы и сравним
        form_data = {
            "text": "Not equal text",
            "group": self.group.id,
        }
        expected_text = form_data["text"]
        # проверим измененное вновь текстовое поле без отправления формы
        self.assertFalse(Post.objects.filter(text=expected_text).exists())

    def test_comment_add(self):
        """Комментарий от авторизованного пользователя успешно создается"""
        form_data = {"text": "Test Comment"}
        expected_url = reverse("add_comment", kwargs={
            "username": PostCreateFormTests.author.username,
            "post_id": PostCreateFormTests.post.id,
        })
        actual_response = self.authorized_client.post(
            expected_url, data=form_data, follow=True,
        )
        self.assertRedirects(actual_response, reverse(
            "post", args=[self.post.author.username, self.post.id]
        ))
        expected_text = form_data["text"]
        # проверим текстовое поле после отправления формы
        self.assertTrue(Comment.objects.filter(text=expected_text).exists())
