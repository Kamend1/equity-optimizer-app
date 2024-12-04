from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import PermissionDenied

from EquityOptimizerApp.accounts.models import Profile
from EquityOptimizerApp.portfolio.models import Portfolio, PortfolioUpvote, PortfolioValueHistory
from EquityOptimizerApp.portfolio.forms import PortfolioForm
from unittest.mock import patch

UserModel = get_user_model()


class TestPersonalPortfolioListView(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(username="testuser", password="testpass")
        self.profile = Profile.objects.create(user=self.user)
        self.client = Client()

    def test_requires_login(self):
        response = self.client.get(reverse("personal-portfolios"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('personal-portfolios')}")

    def test_displays_user_portfolios(self):
        self.client.login(
            username=self.user.username,
            password='testpass',
        )
        Portfolio.objects.create(user=self.user, name="Test Portfolio")
        response = self.client.get(reverse("personal-portfolios"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Portfolio")


class TestPublicPortfolioListView(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(username="testuser", password="testpass")
        self.other_user = UserModel.objects.create_user(username="otheruser", password="otherpass")
        self.client = Client()
        self.public_portfolio_1 = Portfolio.objects.create(user=self.other_user, name="Public Portfolio 1", public=True)
        self.public_portfolio_2 = Portfolio.objects.create(user=self.user, name="User Portfolio", public=True)
        Profile.objects.create(user=self.user)
        Profile.objects.create(user=self.other_user)

    def test_displays_public_portfolios(self):
        self.client.login(
            username=self.user.username,
            password='testpass',
        )

        response = self.client.get(reverse("public-portfolios"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Public Portfolio 1")

    def test_excludes_user_own_portfolios(self):
        self.client.login(
            username=self.user.username,
            password='testpass',
        )

        response = self.client.get(reverse("public-portfolios"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "User Portfolio")


class TestToggleUpvoteView(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(username="testuser", password="testpass")
        self.other_user = UserModel.objects.create_user(username="otheruser", password="otherpass")
        self.portfolio = Portfolio.objects.create(user=self.other_user, name="Portfolio")
        self.client = Client()
        Profile.objects.create(user=self.user)
        Profile.objects.create(user=self.other_user)

    def test_requires_login(self):
        response = self.client.post(reverse("portfolio-toggle-upvote", args=[self.portfolio.id]), HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 302)

    def test_upvote_creates_record(self):
        self.client.login(
            username=self.user.username,
            password='testpass',
        )
        response = self.client.post(reverse("portfolio-toggle-upvote", args=[self.portfolio.id]), HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PortfolioUpvote.objects.count(), 1)

    def test_cannot_upvote_own_portfolio(self):
        self.client.login(
            username=self.other_user.username,
            password='otherpass',
        )
        response = self.client.post(reverse("portfolio-toggle-upvote", args=[self.portfolio.id]), HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 400)


class TestPortfolioDetailView(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(username="testuser", password="testpass")
        self.other_user = UserModel.objects.create_user(username="otheruser", password="otherpass")
        self.portfolio = Portfolio.objects.create(user=self.user, name="Portfolio")
        self.client = Client()
        Profile.objects.create(user=self.user)
        Profile.objects.create(user=self.other_user)

    def test_requires_login(self):
        response = self.client.get(reverse("portfolio-detail", args=[self.portfolio.id]))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('portfolio-detail', args=[self.portfolio.id])}")

    def test_allows_owner_to_view(self):
        self.client.login(
            username=self.user.username,
            password='testpass',
        )
        response = self.client.get(reverse("portfolio-detail", args=[self.portfolio.id]))
        self.assertEqual(response.status_code, 200)

    def test_raises_permission_denied_for_non_owner(self):
        self.client.login(
            username=self.other_user.username,
            password='otherpass',
        )
        response = self.client.get(reverse("portfolio-detail", args=[self.portfolio.id]))
        self.assertEqual(response.status_code, 403)


class TestPortfolioPerformanceView(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(username="testuser", password="testpass")
        self.client = Client()
        Profile.objects.create(user=self.user)

    def test_requires_login(self):
        response = self.client.get(reverse("portfolios-performance"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('portfolios-performance')}")
