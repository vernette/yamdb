import random

from django.conf import settings
from django.db.models import Avg
from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.permissions import (
    AdminPermission, ModeratorPermission, UserReadOnlyPermission
)
from api.serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    GetTokenSerializer, ReviewSerializer, SignUpSerializer,
    TitleSerializer, UserSerializer
)
from reviews.validators import validate_confirmation_code
from reviews.models import Category, Genre, Review, Title, User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminPermission,)
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        methods=('GET', 'PATCH',),
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        instance = self.request.user
        serializer = self.get_serializer(instance)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                instance,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=instance.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuthViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(methods=['POST'],
            detail=False,
            permission_classes=[AllowAny])
    def signup(self, request):
        try:
            serializer = SignUpSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user, created = User.objects.get_or_create(
                **dict(serializer.validated_data)
            )
            user.confirmation_code = self.get_new_confirmation_code()
            user.save()
            self.send_confirmation_code(user)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        except (IntegrityError, serializers.ValidationError) as error:
            return Response(
                error.args[0],
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=['POST'],
            detail=False,
            permission_classes=[AllowAny])
    def token(self, request):
        try:
            serializer = GetTokenSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = get_object_or_404(
                User,
                username=serializer.validated_data['username']
            )
            if validate_confirmation_code(
                user_code=user.confirmation_code,
                request_code=serializer.validated_data['confirmation_code']
            ):
                token = AccessToken.for_user(user)
                return Response(
                    {'token': str(token)},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'error': 'Неверный код подтверждения'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except serializers.ValidationError as error:
            return Response(
                error.args[0],
                status=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def send_confirmation_code(user):
        subject = 'Код подтверждения'
        message = (
            f'Добрый день, {user.username}! \n'
            f'Ваш код подтверждения '
            f'для получения токена на YAMDB: \n'
            f'{user.confirmation_code}'
        )
        user_email = user.email
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user_email])

    @staticmethod
    def get_new_confirmation_code():
        code = ""
        for i in range(6):
            code += str(random.randint(0, 9))
        return code


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [UserReadOnlyPermission | AdminPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filterset_class = TitleFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(rating=Avg('reviews__score'))
        return queryset


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [UserReadOnlyPermission | AdminPermission]
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'name'

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        slug = self.kwargs.get('slug')
        obj = get_object_or_404(queryset, slug=slug)
        self.check_object_permissions(self.request, obj)
        return obj


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [UserReadOnlyPermission | AdminPermission]
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'name'

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        slug = self.kwargs.get('slug')
        obj = get_object_or_404(queryset, slug=slug)
        self.check_object_permissions(self.request, obj)
        return obj


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [
        AdminPermission | IsAuthenticatedOrReadOnly | ModeratorPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_title_id(self):
        return self.kwargs.get('title_id')

    def get_title(self):
        title_id = self.get_title_id()
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def create(self, request, *args, **kwargs):
        title = self.get_title()
        user = self.request.user
        if Review.objects.filter(title=title, author=user).exists():
            return Response(
                {'error': 'Вы уже оставили отзыв на это произведение.'},
                status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        score = serializer.validated_data.get('score')
        if int(score) > 10:
            return Response(
                {'error': 'Оценка не может быть выше 10 баллов.'},
                status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers)

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)

    def update(self, request, *args, **kwargs):
        review = self.get_object()
        if (request.user.is_admin
                or request.user.is_moderator
                or review.author == request.user):
            serializer = self.get_serializer(
                review,
                data=request.data,
                partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        review = self.get_object()
        if (request.user.is_admin
                or request.user.is_moderator
                or review.author == request.user):
            review.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [
        AdminPermission | ModeratorPermission | IsAuthenticatedOrReadOnly
    ]

    def get_review_id(self):
        return self.kwargs.get('review_id'), self.kwargs.get('title_id')

    def get_review(self):
        review_id, title_id = self.get_review_id()
        return get_object_or_404(Review, pk=review_id, title_id=title_id)

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        review = self.get_review()
        user = self.request.user
        serializer.save(author=user, review=review)

    def update(self, request, pk=None, *args, **kwargs):
        comment = self.get_object()
        if comment.author == self.request.user:
            return super().update(request=request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author == self.request.user:
            return super().destroy(request=request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        comment = self.get_object()
        if (comment.author != request.user and not request.user.is_admin
                and not request.user.is_moderator):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(
            comment,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if (request.user.is_admin
                or request.user.is_moderator
                or comment.author == request.user):
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
