from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count

UserModel = get_user_model()


# Create your models here.

class InvestorLevelChoices(models.TextChoices):
    PRO = "Professional", "Professional"
    RETAIL = "Retail", "Retail"
    ELIGIBLE = "Eligible", "Eligible"


class Profile(models.Model):
    profile_image = models.URLField(null=True, blank=True)
    profile_link = models.URLField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    investor_level = models.CharField(max_length=30, choices=InvestorLevelChoices.choices, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    user = models.OneToOneField(to=UserModel, on_delete=models.CASCADE, related_name='profile')

    def total_upvotes(self):
        return self.user.portfolios.filter(public=True).aggregate(total_upvotes=Count('upvotes'))['total_upvotes'] or 0
