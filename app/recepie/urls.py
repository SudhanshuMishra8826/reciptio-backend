"""
URLs for recepie app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from recepie import views

router = DefaultRouter()
router.register('recepie', views.RecepieViewSet, basename='recepie')
router.register('tag', views.TagViewSet, basename='tag')

app_name = 'recepie'

urlpatterns = [
    path('', include(router.urls))
]
