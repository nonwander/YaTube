from django.contrib.auth import get_user_model
from django.db import models
from pytils.translit import slugify

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    description = models.TextField(max_length=200, verbose_name="Описание")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:200]
        super().save(*args, **kwargs)


class Post(models.Model):
    text = models.TextField(
        help_text="Текст поста", verbose_name="Текст поста",
    )
    pub_date = models.DateTimeField(
        "date published", auto_now_add=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts",
        verbose_name="Автор поста", help_text="Автор поста"
    )
    group = models.ForeignKey(
        "Group", on_delete=models.SET_NULL, related_name="posts",
        blank=True, null=True, verbose_name="Сообщество",
        help_text="Выберите группу",
    )
    image = models.ImageField(upload_to="posts/", blank=True, null=True)

    class Meta:
        """сортировка всех записей по заданному полю 'pub_date' """

        ordering = ("-pub_date",)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post, null=True, blank=True, on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Ссылка на пост",
        help_text="Ссылка на пост"
    )
    author = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор комментария",
        help_text="Автор комментария"
    )
    text = models.TextField(
        help_text="Текст комментария", verbose_name="Текст комментария"
    )
    created = models.DateTimeField(
        "date commenting", auto_now_add=True
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
        help_text="Подписчик на автора поста"
    )
    author = models.ForeignKey(
        User, null=True,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
        help_text="Автор интересного поста"
    )

    class Meta:
        """Проверка на уникальность подписки перед сохранением"""
        constraints = [models.UniqueConstraint(
            fields=["author", "user"],
            name="unique_object"
        )]
