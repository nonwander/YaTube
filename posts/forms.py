from django import forms
from django.db import models

from .models import Comment, Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = {"text", "group", "image"}
        labels = {
            "text": "Текст",
            "group": "Группа",
        }
        title = models.CharField(
            verbose_name="Заголовок",
            help_text="Дайте короткое название для новой записи",
            max_length=100,
        )
        help_texts = {
            "text": "Введие текст поста",
            "group": "Выберите группу"
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ["text"]
