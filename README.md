# CS50W Project 2: Commerce (Den Blå Avis Redesign)

## A redesign of Den Blå Avis (DBA), the Danish equivalent of eBay. <br> An informal auction site which allows users to list items, watch items and place bids.

[See the Video](https://youtu.be/BiOrfYFu6-w)<br>

👤 Users can register for accounts

🚲 List items for sale

🧑‍💻 Bid on listings

📣 Message each other via comments on listings

💁 Profile page to display watched, won and bidded-on listings

## Models

The backend is run on Python/Django and the database set up using models for listings, comments, bids and a watchlist.

The models are connected via foreign keys allowing complex lookups and displays of details on each page.

```
class Listings(models.Model):
    title = models.CharField(max_length=32)
    description = models.CharField(max_length=512)
    start_price = models.IntegerField()
    highest_bid = models.IntegerField(default=0)
    highest_bid_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="listing_winner", null=True, default=None)
    image = models.CharField(max_length=128)
    category = models.CharField(max_length=32)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, default=None)
    active = models.BooleanField(default="True")

    def __str__(self):
        return f"{self.title}, {self.description}, {self.start_price}, {self.highest_bid}, {self.image}, {self.category}, {self.user}, {self.start_time}, {self.end_time}"

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

class Watchlist(models.Model):
   listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="watchlist")
   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
   time = models.DateTimeField()

   def __str__(self):
        return f"{self.listing}, {self.user}, {self.time}"
```

## Create a Listing

Registered users can add listings, with details such as: Title, Description, Url address for an image, Start Price and Category.

```
def new_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        image = request.POST["image"]
        start_price = request.POST["start_price"]
        category = request.POST["category"]

        new_listing = Listings(
            title=title,
            description=description,
            image=image,
            start_price=start_price,
            # no bids on creation, so set highest_bid = start_price
            highest_bid=start_price,
            category=category,
            user=request.user,
            start_time=datetime.now(),
        )

        new_listing.save()
        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "auctions/new_listing.html", {
            "categories": categories,
        })
```

### For future updates:
- Ability to upload and view multiple photos for listings (using a url was allowed for the CS50W project)
- Users can set an end-time for the listing, but this could be implemented as a countdown, a la eBay.

## The Index Page

The home page displays all active listings. I wanted to make this page significantly less cluttered than Den Blå Avis.
I borrowed the style idea of individual cards and a slight zoom on hover from DBA.
The nav display has been made cleaner.
The function below allows the listings to be displayed newest first.

```
from operator import attrgetter

def index(request):
    listings = sorted(Listings.objects.all(), key=attrgetter('start_time'), reverse=True)
    return render(request, "auctions/index.html", {
        "listings": listings,
        "categories": categories,
    })
```
### Active listings are filtered from inactive in the html.

```
<div class="index_grid">
    <h2>Latest Listings</h2>
    <div class="listings">
    {% for listing in listings %}
        {% if listing.active == True %}
        <a href="{% url 'listing' listing.id %}">
            <div class="card">
                <img src="{{ listing.image }}">
                <div class="card_details">
                    <h2>{{ listing.title|slice:":15"  }}</h2>
                    <h3>{{ listing.highest_bid|intcomma  }} kr.</h3>
                </div>
            </div>
        </a>
    {% endif %}
    {% empty %}
        <h2>No current listings</h2>
    {% endfor %}
    </div>
```
### For future updates:
- Separate bars for recent, featured categories, last-seen etc.
- Ability to side scroll through the listings, rather than have them all wrap.

## Listing Page

The listing page features three main columns: an image, a list of details (title, description, price etc), and a history.
The history is a joining of the comments and bids categories to provide a message-like display on the side of the listing.

### See listing.html for how the contents of the page dynamically changes depending on which user is viewing the page and the listing status

```
def listing(request, listing_id):
    listing = Listings.objects.get(id=listing_id)
    comments = Comments.objects.filter(listing=listing_id)
    bids = Bids.objects.filter(listing=listing_id)
    bid_count = bids.count()

    # Mergers the data for comments and bids, then sorts by time, to give a history for the listing
    history = sorted(chain(bids, comments), key=attrgetter('time'), reverse=True)

    # Check if the user is watching the listing
    watching = Watchlist.objects.filter(listing=listing, user=request.user)
    if watching.exists():
        watched = True
    else:
        watched = False

    return render(request, "auctions/listing.html", {
        "listing": listing,
        'history': history,
        "bid_count": bid_count,
        "watched": watched,
        "categories": categories,
    })
```

## Categories

Categories for listings are stored as tuples with their respective icon:

```
categories = [
    ("Vehicles", "🚙"),
    ("Books", "📘"),
    ("Home", "🏠"),
    ("Garden", "🪴"),
    ("Clothes", "👗"),
    ("Children", "🧸"),
    ("Sport", "⚽️"),
    ("Boats", "⛵️"),
    ("Bikes", "🚲"),
    ("Electronics", "💻"),
    ("Animals", "🐈"),
    ("Instruments", "🎸"),
    ("Other", "📦")
]
```

## Admin
Visiting /admin in the url will take you to Django's built-in administration allowing listings, comments, bids and watchlists to be edited or deleted:

```
/admin.py

from django.contrib import admin
from .models import Listings, Comments, Bids, Watchlist

admin.site.register(Listings)
admin.site.register(Comments)
admin.site.register(Bids)
admin.site.register(Watchlist)
```

### Note: A few lines of code and initial setup was supplied by CS50W