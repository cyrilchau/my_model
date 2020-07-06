from django.db import models
from urllib.request import urlopen
from django.contrib.gis.db import models as gis_models
from django.contrib.gis import geos
from django.db.models import Manager as GeoManager
from geopy.geocoders.googlev3 import GoogleV3
from geopy.geocoders.googlev3 import GeocoderQueryError
from django.conf import settings
from my_model.utils import unique_slug_generator
from taggit.managers import TaggableManager
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import User
from postgres_copy import CopyManager
# Create your models here.


class Category(models.Model):
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.category

    class Meta:
        db_table = "tbl_Category"

class District(models.Model):
    district = models.CharField(max_length=30)
    class Meta:
        db_table = "tbl_District"
    def __str__(self):
        return self.district

class Shop(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, blank=True, null=True)
    cover_img = models.CharField(max_length=250, blank=True)
    avgscore = models.FloatField(default=0)
    review_count = models.IntegerField(default=0)
    address = models.CharField(max_length=100)
    district = models.ForeignKey(District,on_delete=models.CASCADE)
    city = models.CharField(max_length=30)
    lat = models.CharField(max_length=50, blank=True)
    lon = models.CharField(max_length=50, blank=True)
    location = gis_models.PointField(u"longitude/latitude", srid=4326,
                                     geography=True, blank=True, null=True)
    timeopen = models.CharField(max_length=50, blank=True)
    pricerange = models.CharField(max_length=50, blank=True)
    category = models.ManyToManyField(Category)
    tags = TaggableManager(blank=True)
    objects = CopyManager()

    gis = GeoManager()
    objects = models.Manager()

    class Meta:
        db_table = "tbl_Shop"

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.location:
            address = u'%s %s' % (self.city, self.address)
            address = address.encode('utf-8')
            geocoder = GoogleV3()
            try:
                _, latlon = geocoder.geocode(address)
            except (urlopen, GeocoderQueryError, ValueError):
                pass
            else:
                point = "POINT(%s %s)" % (latlon[1], latlon[0])
                self.location = geos.fromstr(point)
        super(Shop, self).save()


Shop.gis.filter()  # with GIS queries
Shop.objects.filter()  # only standard queries


def slug_generator(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(slug_generator, sender=Shop)


# class ShopCategory(models.Model):
#     shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)

#     class Meta:
#         db_table = "tbl_ShopCategory"


class ShopImage(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    img_url = models.CharField(max_length=250, blank=True)

    class Meta:
        db_table = "tbl_ShopImage"


class Comment(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    rating = models.FloatField(default=1.0)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "tbl_Comment"


class Contact(models.Model):
    sender = models.CharField(max_length=25)
    email = models.EmailField(max_length=254, default='')
    title = models.CharField(max_length=200, null=False)
    body = models.TextField(null=False)
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tbl_Contact"


class Menu(models.Model):
    title = models.CharField(max_length=200, null=False)

    class Meta:
        db_table = "tbl_Menu"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True, default='default.jpg', upload_to='profile_pics')

    class Meta:
        db_table = "tbl_Profile"

