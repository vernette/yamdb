from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title
from reviews.constants import (
    NAME_MAX_LENGTH_LIMIT,
    EMAIL_MAX_LENGTH_LIMIT
)
from reviews.validators import validate_username, validate_email

User = get_user_model()


class GetTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=NAME_MAX_LENGTH_LIMIT,
        required=True
    )
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH_LIMIT,
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        return validate_username(value)


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
        return validate_username(value)

    def validate_email(self, value):
        return validate_email(value)


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

    def validate(self, data):
        if self.context.get('request').method == 'POST':
            if Review.objects.filter(
                author=self.context['request'].user,
                title_id=self.context['view'].kwargs.get('title_id')
            ).exists():
                raise serializers.ValidationError(
                    'Вы не можете создать более одного отзыва '
                    'на одно и то же произведение'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
