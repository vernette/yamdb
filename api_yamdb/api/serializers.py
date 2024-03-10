import re

from rest_framework import serializers
from django.db.models import Avg
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from reviews.models import Title, Category, Genre, Review, Comment


User = get_user_model()


class GetTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class SignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email')


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=(UniqueValidator(queryset=User.objects.all()),)
    )
    email = serializers.EmailField(
        required=True,
        validators=(UniqueValidator(queryset=User.objects.all()),)
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )
        read_only_field = ('role',)


    def validate_username(self, value):
        if value == 'me':
            raise ValidationError(
                'Имя пользователя "me" запрещено!'
            )
        elif re.search(r'^[\w.@+-]+\Z', value) is None:
            raise ValidationError(
                f'Cимволы <{value}> - запрещены для использования в нике!'
            )
        elif len(value) > 150:
            raise ValidationError(
                f'Имя пользователя не может быть длиннее 150 символов!'
            )
        else:
            return value

    def validate_email(self, value):
        if len(value) > 150:
            raise ValidationError(
                f'Адрес электронной почты '
                f'не может быть длиннее 150 символов!'
            )
        else:
            return value


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'

    def get_rating(self, title):
        reviews = Review.objects.filter(title=title)
        average_rating = reviews.aggregate(Avg('score'))['score__avg']
        return round(average_rating) if average_rating else None


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        validators=(UniqueValidator(queryset=Category.objects.all()),),
    )

    class Meta:
        model = Category
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        validators=(UniqueValidator(queryset=Genre.objects.all()),),
    )

    class Meta:
        model = Genre
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        required=False  # Это временная версия до введения системы токенов
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('author',)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        required=False  # Это заглушка до введения системы токенов
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('author',)
