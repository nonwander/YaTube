from django.test import TestCase

from posts.models import Comment, Group, Post, User


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        """ Создаём тестовую запись в БД
        Не указываем значение slug, ждем, что при создании
        оно создастся автоматически из title - метод slugify.
        title сделаем, чтобы после транслитерации он стал более 200 символов
        (буква "ж" транслитерируется в два символа: "zh")
        """
        cls.group = Group.objects.create(
            title="Ж"*200,
            description="Тестовый текст",
        )

    def test_text_convert_to_slug(self):
        """save преобразует в slug содержимое поля title."""
        group = GroupModelTest.group
        actual_slug = group.slug
        expected = "zh"*100
        self.assertEquals(actual_slug, expected)

    def test_text_slug_max_length_not_exceed(self):
        """Длинный slug обрезается и не больше чем slug max_length."""
        group = GroupModelTest.group
        actual_max_length_slug = group._meta.get_field("slug").max_length
        expected_length_slug = (len(group.slug))
        self.assertEquals(actual_max_length_slug, expected_length_slug)

    def test_str_equals_title_group(self):
        """__str__ group - это строчка с содержимым group.title."""
        group = GroupModelTest.group
        expected_group_name = str(group)
        actual_group_title = group.title
        self.assertEquals(actual_group_title, expected_group_name)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_verboses = {
            "title": "Заголовок",
            "description": "Описание",
            "slug": "Slug",
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="TestUser")
        # Создаём длинный тестовый пост в группе
        # В поле text 30 знаков: 5*6=30
        cls.post = Post.objects.create(
            text="Test!"*6,
            author=cls.user,
        )

    def test_str_equals_post_15(self):
        """__str__ модели Post сформировано из первых 15 символов поста."""
        post = PostModelTest.post
        actual_object_name = str(post)
        expected_text = "Test!"*3
        self.assertEquals(actual_object_name, expected_text)

    def test_verbose_name(self):
        """verbose_name в полях Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            "text": "Текст поста",
            "author": "Автор поста",
            "group": "Сообщество",
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            "text": "Текст поста",
            "author": "Автор поста",
            "group": "Выберите группу",
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="TestUser")
        cls.post = Post.objects.create(
            text="Test Post",
            author=cls.user,
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text="Test comment"
        )

    def test_verbose_name(self):
        """verbose_name в полях Comment совпадает с ожидаемым."""
        comment = CommentModelTest.comment
        field_verboses = {
            "post": "Ссылка на пост",
            "author": "Автор комментария",
            "text": "Текст комментария",
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях Comment совпадает с ожидаемым."""
        comment = CommentModelTest.comment
        field_help_texts = {
            "post": "Ссылка на пост",
            "author": "Автор комментария",
            "text": "Текст комментария",
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).help_text, expected)
