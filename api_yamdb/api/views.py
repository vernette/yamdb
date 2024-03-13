from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.mixins import ReviewCommentMixin, GenreCategoryMixin
from api.permissions import AdminPermission, AdminOrReadOnlyPermission
from api.serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    GetTokenSerializer, ReviewSerializer, SignUpSerializer,
    TitleSerializer, UserSerializer
)
from api.utils import send_confirmation_code
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
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


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
            send_confirmation_code(
                user=user,
                confirmation_code=default_token_generator.make_token(user)
            )
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
            if default_token_generator.check_token(
                user=user,
                token=serializer.validated_data['confirmation_code']
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


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [AdminOrReadOnlyPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filterset_class = TitleFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(rating=Avg('reviews__score'))
        return queryset


class CategoryViewSet(GenreCategoryMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(GenreCategoryMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ReviewViewSet(ReviewCommentMixin):
    serializer_class = ReviewSerializer

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(ReviewCommentMixin):
    serializer_class = CommentSerializer

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
