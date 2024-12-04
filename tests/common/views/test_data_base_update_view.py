from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from EquityOptimizerApp.accounts.models import Profile

UserModel = get_user_model()


class TestDatabaseUpdateView(TestCase):
    def setUp(self):
        self.staff_user = UserModel.objects.create_user(username='staffuser', password='staffpass', is_staff=True)
        Profile.objects.create(user=self.staff_user)
        self.non_staff_user = UserModel.objects.create_user(username='nonstaffuser', password='nonstaffpass')
        Profile.objects.create(user=self.non_staff_user)

    def test_non_staff_user_redirected_to_login(self):
        self.client.login(
            username=self.non_staff_user.username,
            password='nonstaffpass',
        )
        response = self.client.get(reverse('database_update'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('database_update')}")

    def test_staff_user_can_access_database_update_view(self):
        self.client.login(
            username=self.staff_user.username,
            password='staffpass',
        )
        response = self.client.get(reverse('database_update'))
        self.assertEqual(response.status_code, 200)
