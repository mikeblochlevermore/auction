# Generated by Django 4.2.2 on 2023-08-01 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_listings_highest_bid_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='listings',
            name='active',
            field=models.BooleanField(default='True'),
        ),
    ]
