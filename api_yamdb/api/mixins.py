from rest_framework import filters, mixins, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.permissions import (
    AdminOrReadOnlyPermission,
    AuthorModeratorAdminPermission
)


class ReviewCommentMixin(viewsets.ModelViewSet):
    permission_classes = (AuthorModeratorAdminPermission,
                          IsAuthenticatedOrReadOnly)
    http_method_names = ['get', 'post', 'patch', 'delete']


class GenreCategoryMixin(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (AdminOrReadOnlyPermission,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
