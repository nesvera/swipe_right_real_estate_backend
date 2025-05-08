import uuid

from django.db import models


class Agency(models.Model):
    """Model to store real estate agency info"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    creci = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    address_street = models.CharField(max_length=100)
    address_number = models.CharField(max_length=40)
    contact_number_1 = models.CharField(max_length=20)
    contact_number_2 = models.CharField(max_length=20)
    contact_whatsapp = models.CharField(max_length=20)
    logo_url = models.CharField(max_length=500)
    profile_url = models.CharField(max_length=500)
