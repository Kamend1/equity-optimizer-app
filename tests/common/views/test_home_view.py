from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from EquityOptimizerApp.accounts.models import Profile

UserModel = get_user_model()


class TestHomeView(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(username='testuser', password='testpass')
        self.profile = Profile.objects.create(user=self.user)
        print(f"User: {self.user}, PK: {self.user.pk}")

    def test_anonymous_user_redirects_to_login(self):
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('home')}")

    def test_authenticated_user_sees_home(self):
        self.client.login(
            username=self.user.username,
            password='testpass',
        )
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

