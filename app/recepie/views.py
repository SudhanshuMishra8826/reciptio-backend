"""
This module contains the views for the recepie API
"""
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Recepie, Tag
from recepie import serializers


class RecepieViewSet(viewsets.ModelViewSet):
    """
    Views for recepie API
    """
    serializer_class = serializers.RecepieDetailSerializer
    queryset = Recepie.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Retrieve the recepies for the authenticated user
        """
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """
        Return appropriate serializer class
        """
        if self.action == 'list':
            return serializers.RecipieSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """
        Create a new recepie
        """
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """
        Update a recepie
        """
        print("attempt", self.request.data, serializer.validated_data,
              self.serializer_class)
        serializer.save(user=self.request.user)


class TagViewSet(mixins.UpdateModelMixin, mixins.CreateModelMixin,
                 mixins.DestroyModelMixin, viewsets.GenericViewSet,
                 mixins.ListModelMixin):
    """
    Views for tag API
    """
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Retrieve the tags for the authenticated user
        """
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """
        Create a new tag
        """
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """
        Update a tag
        """
        serializer.save(user=self.request.user)
