import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField

from user.models import User
from real_estate.models import RealEstate


class Filter(models.Model):
    """Model with parameters used in the filter for real estate"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True
    )
    property_type = ArrayField(
        models.CharField(max_length=15, choices=RealEstate.PropertyType), null=True
    )
    transaction_type = ArrayField(
        models.CharField(max_length=15, choices=RealEstate.TransactionType), null=True
    )
    city = ArrayField(models.CharField(max_length=100))
    neighborhood = ArrayField(models.CharField(max_length=100))
    bedroom_quantity = ArrayField(models.IntegerField())
    suite_quantity = ArrayField(models.IntegerField())
    bathroom_quantity = ArrayField(models.IntegerField())
    garage_slots_quantity = ArrayField(models.IntegerField())
    min_price = models.FloatField()
    max_price = models.FloatField()
    min_area = models.FloatField()
    max_area = models.FloatField()


class Search(models.Model):
    """Model used to store searches from user"""

    # Search will be performed against database in background
    # The following are states in order that a search will go through
    class QueryStatus(models.TextChoices):
        NOT_STARTED = "not_started", "not started"
        STARTED = "started", "started"
        PARTIAL = "partial", "partial"
        FINISHED = "finished", "finished"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True
    )
    filter = models.ForeignKey(Filter, on_delete=models.CASCADE)
    query_status = models.CharField(
        max_length=15, choices=QueryStatus, default=QueryStatus.NOT_STARTED
    )
    # TODO - check if is possible to delete this, and only count search results
    number_real_estate_found = models.IntegerField(default=0)


class SearchResultRealEstate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    search = models.ForeignKey(Search, on_delete=models.CASCADE)
    real_estate = models.ForeignKey(RealEstate, on_delete=models.CASCADE)
