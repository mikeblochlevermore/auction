from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listings(models.Model):
    title = models.CharField(max_length=32)
    description = models.CharField(max_length=128)
    start_bid = models.IntegerField()
    image = models.CharField(max_length=128)
    category = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.title}, {self.description}, {self.start_bid}, {self.image}, {self.category}"

class Comments(models.Model):
   listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="comments", null=True)
   comment = models.CharField(max_length=128)
   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
   time = models.DateTimeField()

   def __str__(self):
        return f"{self.listing}, {self.comment}, {self.user}, {self.time}"