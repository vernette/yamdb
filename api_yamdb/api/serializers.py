import re

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title

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
                'Cимволы <{value}> - запрещены для использования в нике!'
            )
        elif len(value) > 150:
            raise ValidationError(
                'Имя пользователя не может быть длиннее 150 символов!'
            )
        else:
            return value

    def validate_email(self, value):
        if len(value) > 150:
            raise ValidationError(
                'Адрес электронной почты '
                'не может быть длиннее 150 символов!'
            )
        else:
            return value


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        allow_empty=False,
        many=True
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category'] = {
            'name': instance.category.name,
            'slug': instance.category.slug
        }
        representation['genre'] = [
            {
                'name': genre.name,
                'slug': genre.slug
            } for genre in instance.genre.all()
        ]
        return representation


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
