from django.contrib import admin
from .models import Listings, Comments

# Register your models here.
admin.site.register(Listings)
admin.site.register(Comments)