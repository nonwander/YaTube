from datetime import datetime

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username="TestUser")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title="Test title",
            description="Test description",
            slug="Test_Slug",
        )

    def setUp(self):
        for number in range(13):
            self.post = Post.objects.create(
                text=f"Post {number}",
                pub_date=datetime.now(),
                author=PaginatorViewsTest.author,
                group=PaginatorViewsTest.group,
            )

    def test_index_first_page_containse_ten_records(self):
        response = self.client.get(reverse("index"))
        # Проверка: количество постов на первой странице равно 10.
        actual_len = len(response.context.get("page").object_list)
        self.assertEqual(actual_len, 10)

    def test_index_second_page_containse_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse("index") + "?page=2")
        actual_len = len(response.context.get("page").object_list)
        self.assertEqual(actual_len, 3)
