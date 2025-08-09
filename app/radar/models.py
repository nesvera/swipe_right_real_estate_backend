import uuid

from django.db import models

from django.contrib.auth import get_user_model
from search.models import Search
from real_estate.models import RealEstate


class Radar(models.Model):
    """Radar model
    This model will keep reference to a search
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    search = models.ForeignKey(Search, on_delete=models.CASCADE)


class RadarRealEstate(models.Model):
    """
    This model relates a real estate found in a search with user assessment
    """

    class Preference(models.TextChoices):
        LIKE = "like", "like"
        DISLIKE = "dislike", "dislike"
        PENDING = "pending", "pending"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    radar = models.ForeignKey(Radar, on_delete=models.CASCADE)
    real_estate = models.ForeignKey(RealEstate, on_delete=models.CASCADE)
    updated_real_estate_at = models.DateTimeField(auto_now_add=True)
    removed_at = models.DateTimeField(null=True)
    viewed_at = models.DateTimeField(null=True)
    preference = models.CharField(
        max_length=10, choices=Preference, default=Preference.PENDING
    )
