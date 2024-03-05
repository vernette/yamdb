from rest_framework import viewsets
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination

from reviews.models import Title, Category, Genre, Review
from .serializers import (
    TitleSerializer, CategorySerializer, GenreSerializer, ReviewSerializer,
    CommentSerializer
)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination

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
