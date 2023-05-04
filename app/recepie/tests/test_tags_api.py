"""
Tests for tags API
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from core.models import Tag
from recepie.serializers import TagSerializer
from rest_framework.test import APIClient

TAG_URL = reverse('recepie:tag-list')


def create_user(**params):
    """Helper function to create user"""
    return get_user_model().objects.create_user(**params)

def detail_url(tag_id):
    """Return tag detail URL"""
    return reverse('recepie:tag-detail', args=[tag_id])


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        payload = {
            "email": 'test@example.com',
            "password": 'testpass123'
        }
        self.user = create_user(**payload)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')
        res = self.client.get(TAG_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for authenticated user"""
        payload = {
            "email": 'user2@example.com',
            "password": 'testpass123'
        }
        user2 = create_user(**payload)
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')
        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_tag_update(self):
        """Test updating a tag"""
        tag = Tag.objects.create(user=self.user, name='Vegan')
        payload = {'name': 'Updated name'}
        url = detail_url(tag.id)
        self.client.patch(url, payload)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_tag_delete(self):
        """Test deleting a tag"""
        tag = Tag.objects.create(user=self.user, name='Vegan')
        url = detail_url(tag.id)
        self.client.delete(url)
        self.assertEqual(Tag.objects.count(), 0)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {'name': 'Test tag'}
        self.client.post(TAG_URL, payload)
        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

