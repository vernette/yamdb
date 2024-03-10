from django.contrib import admin
from django.contrib.auth import get_user_model

from reviews.models import Category, Genre, Title, Review, Comment


admin.site.register(get_user_model())
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Title)
admin.site.register(Review)
admin.site.register(Comment)
