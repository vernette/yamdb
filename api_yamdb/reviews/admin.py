from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .models import Category, Comment, Genre, Review, Title, User


admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': (
            'first_name',
            'last_name',
            'email',
            'role',
        )}),
        ('Прочее', {'fields': (
            'bio',
        )}),
        ('Права доступа', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
            'user_permissions',
        )}),
        ('Даты', {'fields': (
            'last_login',
            'date_joined',
        )}),
    )
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'bio',
        'role',
    )
    list_editable = ('role',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'year', 'description', 'get_genres', 'category',
    )
    list_display_links = ('name', 'get_genres',)
    list_editable = ('category',)

    @admin.display(description='Жанр')
    def get_genres(self, obj):
        return ', '.join([str(genre) for genre in obj.genre.all()])


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug',)
    list_display_links = ('name', 'slug',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug',)
    list_display_links = ('name', 'slug',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'title', 'author', 'pub_date', 'score',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'author', 'pub_date', 'review',)
