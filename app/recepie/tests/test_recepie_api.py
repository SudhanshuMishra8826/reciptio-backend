"""
Test cases for recepie api
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recepie, Tag
from recepie.serializers import RecipieSerializer, RecepieDetailSerializer


def detail_url(recepie_id):
    """Helper function to create recepie detail url"""
    return reverse('recepie:recepie-detail', args=[recepie_id])


def create_recepie(user, **params):
    """Helper function to create recepie"""
    defaults = {
        'title': 'Test recepie',
        'description': 'Test description',
        'price': Decimal(10.00),
        'time_minutes': 5,
        'link': 'https://www.google.com'
    }
    defaults.update(params)
    return Recepie.objects.create(user=user, **defaults)


def create_user(**params):
    """Helper function to create user"""
    return get_user_model().objects.create_user(**params)


def create_tag(user, name='Main course'):
    """Helper function to create tag"""
    return Tag.objects.create(user=user, name=name)


class PublicRecepieApiTests(TestCase):
    """Test cases for public recepie api"""

    def setUp(self):
        """Setup test cases"""
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        url = reverse('recepie:recepie-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecepieApiTests(TestCase):
    """Test cases for private recepie api"""

    def setUp(self):
        """Setup test cases"""
        self.client = APIClient()
        payload = {
            'email': 'test@example.com',
            'password': 'testpass',
            'name': 'Test name'
        }
        self.user = create_user(**payload)
        self.client.force_authenticate(self.user)

    def test_retrieve_recepies(self):
        """Test retrieving a list of recepies"""
        create_recepie(user=self.user)
        create_recepie(user=self.user)
        url = reverse('recepie:recepie-list')
        recepies = Recepie.objects.all().order_by('-id')
        serializer = RecipieSerializer(recepies, many=True)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recepies_limited_to_user(self):
        """Test that recepies returned are for the authenticated user"""
        payload = {
            'email': 'test2@example.com',
            'password': 'testpass123',
            'name': 'Test name'
        }
        user2 = create_user(**payload)
        create_recepie(user=user2)
        create_recepie(user=self.user)
        url = reverse('recepie:recepie-list')
        res = self.client.get(url)
        recepies = Recepie.objects.filter(user=self.user)
        serializer = RecipieSerializer(recepies, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recepie_detail(self):
        """Test viewing a recepie detail"""
        recepie = create_recepie(user=self.user)
        url = detail_url(recepie.id)
        serializer = RecepieDetailSerializer(recepie)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recepie(self):
        """Test creating recepie"""
        payload = {
            'title': 'Test recepie',
            'description': 'Test description',
            'price': Decimal(10.00),
            'time_minutes': 5,
            'link': 'https://www.google.com'

        }
        url = reverse('recepie:recepie-list')
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recepie = Recepie.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recepie, key))
        self.assertEqual(recepie.user, self.user)

    def test_partial_update_recepie(self):
        """Test updating a recepie with patch"""
        recepie = create_recepie(user=self.user)
        payload = {'title': 'New title', 'description': 'New description'}
        url = detail_url(recepie.id)
        self.client.patch(url, payload)
        recepie.refresh_from_db()
        self.assertEqual(recepie.title, payload['title'])
        self.assertEqual(recepie.description, payload['description'])

    def test_full_update_recepie(self):
        """ Test updating a recepie with put"""
        recepie = create_recepie(user=self.user)
        payload = {
            'title': 'New title',
            'description': 'New description',
            'price': Decimal(10.00),
            'time_minutes': 5,
            'link': 'https://www.google.com'
        }
        url = detail_url(recepie.id)
        self.client.put(url, payload)
        recepie.refresh_from_db()
        self.assertEqual(recepie.title, payload['title'])
        self.assertEqual(recepie.description, payload['description'])
        self.assertEqual(recepie.price, payload['price'])
        self.assertEqual(recepie.time_minutes, payload['time_minutes'])
        self.assertEqual(recepie.link, payload['link'])

    def test_update_user_returns_error(self):
        """Test that updating user returns error"""
        recepie = create_recepie(user=self.user)
        payload = {'user': 10}
        url = detail_url(recepie.id)
        self.client.patch(url, payload)
        recepie.refresh_from_db()
        self.assertEqual(recepie.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe"""
        recepie = create_recepie(user=self.user)
        url = detail_url(recepie.id)
        self.client.delete(url)
        recepie_exists = Recepie.objects.filter(id=recepie.id).exists()
        self.assertFalse(recepie_exists)

    def test_recipe_other_user_reipe(self):
        """Test that other user cannot delete recipe"""
        new_user = create_user(email='user2@example.com', password='testpass')
        recepie = create_recepie(user=new_user)
        url = detail_url(recepie.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        recepie_exists = Recepie.objects.filter(id=recepie.id).exists()
        self.assertTrue(recepie_exists)

    def test_create_recipe_with_new_tags(self):
        """ Test creating recipe api with new tags """
        payload = {
            'title': 'thai curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'description': 'test description',
            'tags': [
                {'name': 'thai'},
                {'name': 'dinner'}
            ]
        }
        url = reverse('recepie:recepie-list')
        res = self.client.post(url, payload, format='json')
        print(res.data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recepie = Recepie.objects.get(id=res.data['id'])
        tags = recepie.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tags[0].name, 'thai')
        self.assertIn(tags[1].name, 'dinner')

    def test_create_recipe_with_existing_tags(self):
        tag_indian = create_tag(user=self.user, name='indian')
        payload = {
            'title': 'thai curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'description': 'test description',
            'tags': [
                {'name': 'thai'},
                {'name': 'indian'}
            ]
        }
        url = reverse('recepie:recepie-list')
        res = self.client.post(url, payload, format='json')
        print(res.data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recepie = Recepie.objects.get(id=res.data['id'])
        tags = recepie.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag_indian, tags)
        for tag in payload['tags']:
            self.assertIn(tag['name'], tags.values_list('name', flat=True))

    def test_create_tag_on_update(self):
        recepie = create_recepie(user=self.user)
        payload = {
            'tags': [{
                'name': 'indian'
            }]
        }
        url = detail_url(recepie.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.filter(user=self.user,
                                     name=payload['tags'][0]['name']).first()
        self.assertIn(new_tag, recepie.tags.all())

    def test_update_recipe_assign_tag(self):
        recepie = create_recepie(user=self.user)
        tag1 = create_tag(user=self.user, name='indian')
        tag2 = create_tag(user=self.user, name='chinese')
        recepie.tags.add(tag1)
        payload = {
            'tags': [
                {'name': 'chinese'}
            ]
        }
        url = detail_url(recepie.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn(tag2, recepie.tags.all())
        self.assertNotIn(tag1, recepie.tags.all())

    def test_clear_recipe_tags(self):
        recepie = create_recepie(user=self.user)
        tag1 = create_tag(user=self.user, name='indian')
        recepie.tags.add(tag1)
        payload = {
            'tags': []
        }
        url = detail_url(recepie.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recepie.tags.count(), 0)
