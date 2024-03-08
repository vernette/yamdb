import random
from django.core.mail import send_mail
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import LimitOffsetPagination

from reviews.models import Title, Category, Genre, Review, User
from .serializers import (
    TitleSerializer, CategorySerializer, GenreSerializer, ReviewSerializer,
    CommentSerializer, UserSerializer, GetTokenSerializer, SignUpSerializer
)
from .permissions import (
    AdminOrUserOrReadOnly,
    AdminOrModeratorOrAuthorPermission
)

import api_yamdb.settings as settings


class AuthViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(methods=['POST'],
            detail=False,
            permission_classes=[AllowAny])
    def signup(self, request):
        user = User.objects.filter(
            username=request.data.get('username'),
            email=request.data.get('email')
        ).first()

        if user:
            serializer = SignUpSerializer(user, data=request.data)
        else:
            serializer = SignUpSerializer(data=request.data)

        if serializer.is_valid():
            serializer.validated_data['confirmation_code'] = \
                self.get_new_confirmation_code()
            user = serializer.save()
            self.send_confirmation_code(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'],
            detail=False,
            permission_classes=[AllowAny])
    def token(self, request):
        serializer = GetTokenSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.data['username']
            user = get_object_or_404(User, username=username)
            conf_code = user.confirmation_code

            if conf_code != serializer.data['confirmation_code']:
                return Response(
                    'Неверный код подтверждения!',
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                token = RefreshToken.for_user(user)
                return Response(
                    {'token': str(token)},
                    status=status.HTTP_201_CREATED
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    permission_classes = (AdminOrUserOrReadOnly,)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdminOrUserOrReadOnly,)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdminOrUserOrReadOnly,)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AdminOrModeratorOrAuthorPermission,)

    def get_title_id(self):
        return self.kwargs.get('title_id')

    def get_title(self):
        title_id = self.get_title_id()
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        User = get_user_model()  # Это заглушка до введения системы токенов
        test_user = User.objects.get(username='test')
        serializer.save(author=test_user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AdminOrModeratorOrAuthorPermission,)

    def get_review_id(self):
        return self.kwargs.get('review_id')

    def get_review(self):
        review_id = self.get_review_id()
        return get_object_or_404(Review, pk=review_id)

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        review = self.get_review()
        User = get_user_model()  # Это заглушка до введения системы токенов
        test_user = User.objects.get(username='test')
        serializer.save(author=test_user, review=review)
