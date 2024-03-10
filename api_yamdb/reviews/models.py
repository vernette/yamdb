from django.db import models
from django.contrib.auth.models import AbstractUser

from .constants import TEXT_LENGTH_LIMIT
from .validators import validate_username

ROLE_CHOICES = (
    ('admin', 'Админ'),
    ('moderator', 'Модератор'),
    ('user', 'Пользователь')
)


class User(AbstractUser):
    username = models.CharField(
        validators=(validate_username,),
        max_length=150,
        unique=True,
        blank=False,
        null=False
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )
    bio = models.TextField(
        'биография',
        blank=True,
        null=True
    )
    role = models.CharField(
        'роль',
        max_length=20,
        choices=ROLE_CHOICES,
        default='user'
    )
    confirmation_code = models.CharField(
        'код подтверждения',
        max_length=255,
        null=True,
        blank=False
    )

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_staff or self.is_superuser

    @property
    def is_user(self):
        return self.role == 'user'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50)

    class Meta:
        verbose_name = 'категория (тип) произведения'
        verbose_name_plural = 'Категории (типы) произведений'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50)

    class Meta:
        verbose_name = 'жанр произведения'
        verbose_name_plural = 'Жанры произведений'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    year = models.IntegerField(verbose_name='Год выпуска')
    description = models.TextField(verbose_name='Описание', null=True)
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Slug жанра'
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Slug категории',
        on_delete=models.SET_NULL,
        null=True,
        db_column='category'
    )
    rating = models.IntegerField(
        verbose_name='Средний рейтинг',
        default=0,
        null=True
    )

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
        related_name='reviews'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='reviews',
        db_column='author'
    )
    score = models.IntegerField(
        verbose_name='Рейтинг',
        default=0
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'{self.author}: {self.text}'[:TEXT_LENGTH_LIMIT]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments',
        db_column='author'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        db_index=True
    )
    text = models.TextField(verbose_name='Текст')

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.author}: {self.text}'[:TEXT_LENGTH_LIMIT]
