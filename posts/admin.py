from django.contrib import admin

from .models import Comment, Group, Post


class CommentsAdmin(admin.ModelAdmin):
    list_display = ("author", "text")
    search_fields = ("text",)
    empty_value_display = "-пусто-"


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author",)
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "description", "title", "slug",)
    search_fields = ("description",)
    empty_value_display = "-пусто-"


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentsAdmin)
