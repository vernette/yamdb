from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from reviews.constants import (
    TEXT_LENGTH_LIMIT, MIN_RATING_VALUE, MAX_RATING_VALUE,
    NAME_MAX_LENGTH_LIMIT, EMAIL_MAX_LENGTH_LIMIT, MIN_YEAR_VALUE,
    MODEL_NAME_LENGTH_LIMIT
)
from reviews.validators import validate_username, validate_current_year


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'

    ROLE_CHOICES = (
        (ADMIN, 'Админ'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь')
    )

    username = models.CharField(
        'имя пользователя',
        validators=(validate_username,),
        max_length=NAME_MAX_LENGTH_LIMIT,
        unique=True,
        null=False
    )
    email = models.EmailField(
        'адрес электронной почты',
        max_length=EMAIL_MAX_LENGTH_LIMIT,
        unique=True,
        null=False
    )
    bio = models.TextField(
        'биография',
        blank=True,
        null=True
    )
    role = models.CharField(
        'роль',
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER
    )

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff or self.is_superuser

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)


class BaseNamedSlugModel(models.Model):
    name = models.CharField(
        max_length=MODEL_NAME_LENGTH_LIMIT,
        verbose_name='Название'
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True
    )

    class Meta:
        abstract = True
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Category(BaseNamedSlugModel):

    class Meta(BaseNamedSlugModel.Meta):
        verbose_name = 'категория (тип) произведения'
        verbose_name_plural = 'Категории (типы) произведений'


class Genre(BaseNamedSlugModel):

    class Meta(BaseNamedSlugModel.Meta):
        verbose_name = 'жанр произведения'
        verbose_name_plural = 'Жанры произведений'


class Title(models.Model):
    name = models.CharField(
        max_length=MODEL_NAME_LENGTH_LIMIT,
        verbose_name='Название'
    )
    year = models.SmallIntegerField(
        verbose_name='Год выпуска',
        validators=[
            MinValueValidator(
                MIN_YEAR_VALUE,
                message=f'Год не может быть меньше {MIN_YEAR_VALUE}.'
            ),
            validate_current_year
        ]
    )
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

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class AbstractUserContent(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='%(class)s_related',
        related_query_name='%(class)ss',
        db_column='author'
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.author}: {self.text}'[:TEXT_LENGTH_LIMIT]


class Review(AbstractUserContent):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
        related_name='reviews'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Рейтинг',
        validators=[
            MinValueValidator(
                MIN_RATING_VALUE,
                message=f'Рейтинг не может быть меньше {MIN_RATING_VALUE}.'
            ),
            MaxValueValidator(
                MAX_RATING_VALUE,
                message=f'Рейтинг не может быть больше  {MAX_RATING_VALUE}.'
            )
        ],
    )

    class Meta(AbstractUserContent.Meta):
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            UniqueConstraint(
                fields=['title', 'author'],
                name='unique_title_author'
            ),
        ]


class Comment(AbstractUserContent):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
        related_name='comments'
    )

    class Meta(AbstractUserContent.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
