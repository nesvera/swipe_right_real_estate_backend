import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField

from real_estate_agency.models import Agency


class RealEstate(models.Model):
    """Model to store real estate"""

    class PropertyType(models.TextChoices):
        """Enum for types of real estates"""

        APARTMENT = "apartment", "apartment"
        HOUSE = "house", "house"
        TERRAIN = "terrain", "terrain"
        OFFICE = "office", "office"
        STORE = "store", "store"
        WAREHOUSE = "warehouse", "warehouse"
        RURAL = "rural", "rural"

    class TransactionType(models.TextChoices):
        """Enum to define which kind of transaction is accepted"""

        BUY = "buy", "buy"
        RENT = "rent", "rent"

    def get_images_url_default():
        return list()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    reference_code = models.CharField(max_length=50)
    property_type = models.CharField(
        max_length=15, choices=PropertyType, default=PropertyType.APARTMENT
    )
    transaction_type = models.CharField(
        max_length=15, choices=TransactionType, default=TransactionType.BUY
    )
    city = models.CharField(max_length=100)
    neighborhood = models.CharField(max_length=100)
    bedroom_quantity = models.IntegerField()
    suite_quantity = models.IntegerField()
    bathroom_quantity = models.IntegerField()
    garage_slots_quantity = models.IntegerField()
    price = models.FloatField()
    area = models.FloatField()
    area_total = models.FloatField()
    available = models.BooleanField()
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)
    cond_price = models.FloatField()
    description = models.CharField(max_length=2000)
    images_url = ArrayField(
        models.CharField(max_length=250, default=""),
        default=get_images_url_default,
        size=50,
    )
    updated_at = models.DateTimeField(auto_now=True)
    url = models.CharField(max_length=250)


class RealEstateUpdate(models.Model):
    """Model to keep track of updates of real estate information"""

    class Update(models.TextChoices):
        """Enum to define updates on real estate listing"""

        PRICE = "price", "price"
        AVAILABILITY = "availability", "availability"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    update = ArrayField(models.CharField(max_length=15, choices=Update))
    created_at = models.DateTimeField(auto_now_add=True)
