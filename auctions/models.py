from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listings(models.Model):
    title = models.CharField(max_length=32)
    description = models.CharField(max_length=128)
    start_price = models.IntegerField()
    image = models.CharField(max_length=128)
    category = models.CharField(max_length=32)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.title}, {self.description}, {self.start_price}, {self.image}, {self.category}, {self.user}, {self.start_time}, {self.end_time}"

class Comments(models.Model):
   listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="comments")
   comment = models.CharField(max_length=128)
   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
   time = models.DateTimeField()

   def __str__(self):
        return f"{self.listing}, {self.comment}, {self.user}, {self.time}"

class Bids(models.Model):
   listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="bids")
   bid = models.IntegerField()
   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
   time = models.DateTimeField()

   def __str__(self):
        return f"{self.listing}, {self.bid}, {self.user}, {self.time}"