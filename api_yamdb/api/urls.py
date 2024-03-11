from django.urls import include, path
from rest_framework import routers

from .views import (
    AuthViewSet, CategoryViewSet, CommentViewSet, GenreViewSet,
    ReviewViewSet, TitleViewSet, UserViewSet
)

router_v1 = routers.DefaultRouter()
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
router_v1.register(
    'auth',
    AuthViewSet,
    basename='auth'
)
router_v1.register(
    'users',
    UserViewSet,
    basename='users'
)


urlpatterns = [
    path('v1/categories/<slug:slug>/', CategoryViewSet.as_view({
        'delete': 'destroy'
    }), name='category-detail'),
    path('v1/genres/<slug:slug>/', GenreViewSet.as_view({
        'delete': 'destroy'
    }), name='genre-detail'),
    path('v1/', include(router_v1.urls)),
]
