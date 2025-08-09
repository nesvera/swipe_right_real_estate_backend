import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField

from django.contrib.auth import get_user_model
from radar.models import RadarRealEstate


class RadarRealEstateReview(models.Model):
    """
    Used to store review from user about a real estate inside a filter assessment
    """

    class Tags(models.TextChoices):
        PAINT = "paint", "paint"
        SPACE = "space", "space"
        CONDO_FEE = "condo fee", "condo fee"
        PRICE = "price", "price"
        FINISHING = "finishing", "finishing"
        FLOORS = "floors", "floors"
        CEILING = "ceiling", "ceiling"
        MOLDINGS = "moldings", "moldings"
        NATURAL_LIGHT = "natural light", "natural light"
        VENTILATION = "ventilation", "ventilation"
        WINDOWS = "windows", "windows"
        DOORS = "doors", "doors"
        CLOSETS = "closets", "closets"
        BUILT_IN_CABINETS = "built-in cabinets", "built-in cabinets"
        KITCHEN_COUNTER = "kitchen counter", "kitchen counter"
        BATHROOM_COUNTERS = "bathroom counters", "bathroom counters"
        AIR_CONDITIONING = "air conditioning", "air conditioning"
        HEATING = "heating", "heating"
        FIREPLACE = "fireplace", "fireplace"
        VIEW = "view", "view"
        BALCONY = "balcony", "balcony"
        GARDEN = "garden", "garden"
        LANDSCAPING = "landscaping", "landscaping"
        GARAGE_SPACES = "garage spaces", "garage spaces"
        GUEST_PARKING = "guest parking", "guest parking"
        SOCIAL_ELEVATOR = "social elevator", "social elevator"
        SERVICE_ELEVATOR = "service elevator", "service elevator"
        POOL = "pool", "pool"
        PARTY_ROOM = "party room", "party room"
        GAME_ROOM = "game room", "game room"
        KIDS_ROOM = "kids room", "kids room"
        PLAYGROUND = "playground", "playground"
        PET_AREA = "pet area", "pet area"
        PET_WASH = "pet wash", "pet wash"
        MINI_MARKET = "mini market", "mini market"
        NEAR_SHOPPING_MALL = "near shopping mall", "near shopping mall"
        NEAR_SUPERMARKET = "near supermarket", "near supermarket"
        NEAR_BAKERY = "near bakery", "near bakery"
        NEAR_PHARMACY = "near pharmacy", "near pharmacy"
        NEAR_BANKS = "near banks", "near banks"
        NEAR_PARK = "near park", "near park"
        NEAR_BEACH = "near beach", "near beach"
        NEAR_SCHOOLS = "near schools", "near schools"
        NEAR_COLLEGES = "near colleges", "near colleges"
        QUIET_NEIGHBORHOOD = "quiet neighborhood", "quiet neighborhood"
        NEAR_HOSPITAL = "near hospital", "near hospital"
        NEAR_CLINICS = "near clinics", "near clinics"
        NEAR_RESTAURANTS = "near restaurants", "near restaurants"
        NEAR_CAFES = "near cafes", "near cafes"
        NEAR_CINEMA = "near cinema", "near cinema"
        NEAR_CULTURAL_CENTERS = "near cultural centers", "near cultural centers"
        NEAR_GYM = "near gym", "near gym"
        NEAR_GAS_STATION = "near gas station", "near gas station"
        COST_BENEFIT = "cost benefit", "cost benefit"
        GOOD_FOR_INVESTMENT = "good for investment", "good for investment"
        SOLAR_PANELS = "solar panels", "solar panels"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    radar_real_estate = models.ForeignKey(RadarRealEstate, on_delete=models.CASCADE)
    preference = models.CharField(
        max_length=10,
        choices=RadarRealEstate.Preference,
        default=RadarRealEstate.Preference.PENDING,
    )
    rating = models.IntegerField()
    good_tags = ArrayField(
        models.CharField(max_length=32, choices=Tags), size=10, null=True
    )
    bad_tags = ArrayField(
        models.CharField(max_length=32, choices=Tags), size=10, null=True
    )
    user_notes = models.CharField(max_length=250, default="")
