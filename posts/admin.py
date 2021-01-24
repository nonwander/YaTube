from django.contrib import admin

from .models import Comment, Follow, Group, Post


class CommentsAdmin(admin.ModelAdmin):
    list_display = ("author", "text", "post")
    search_fields = ("text", "post",)
    list_filter = ("author",)
    empty_value_display = "-пусто-"


class FollowAdmin(admin.ModelAdmin):
    list_display = ("author", "user",)
    search_fields = ("author", "user",)
    list_filter = ("author", "user",)
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


admin.site.register(Comment, CommentsAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Post, PostAdmin)
