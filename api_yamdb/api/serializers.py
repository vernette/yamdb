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
    category = serializers.SlugRelatedField(slug_field='slug', queryset=Category.objects.all())
    genre = serializers.SlugRelatedField(slug_field='slug', queryset=Genre.objects.all(), many=True)

    class Meta:
        model = Title
        fields = '__all__'

    def get_rating(self, title):
        reviews = Review.objects.filter(title=title)
        average_rating = reviews.aggregate(Avg('score'))['score__avg']
        return round(average_rating) if average_rating else None

    def validate_name(self, value):
        if len(value) > 256:
            raise ValidationError(
                f'Название произведения не может быть длиннее 256 символов!'
            )
        return value


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        max_length=50,
        validators=[UniqueValidator(queryset=Category.objects.all())]
    )

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')

    def create(self, validated_data):
        slug = validated_data.get('slug')
        if len(slug) > 50:
            raise serializers.ValidationError('Длина slug не должна превышать 50 символов.')
        if Category.objects.filter(slug=slug).exists():
            raise serializers.ValidationError('Категория с таким slug уже существует.')
        return super().create(validated_data)


class GenreSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        max_length=50,
        validators=(UniqueValidator(queryset=Genre.objects.all()),),
    )

    class Meta:
        model = Genre
        fields = ('id', 'name', 'slug')

    def create(self, validated_data):
        slug = validated_data.get('slug')
        if len(slug) > 50:
            raise serializers.ValidationError('Длина slug не должна превышать 50 символов.')
        if Genre.objects.filter(slug=slug).exists():
            raise serializers.ValidationError('Жанр с таким slug уже существует.')
        return super().create(validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    # author = serializers.SlugRelatedField(
    #     slug_field='username',
    #     queryset=User.objects.all()
    # )

    class Meta:
        model = Review
        fields = ('id', 'text', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('author',)
