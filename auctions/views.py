from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime

from .models import User, Listings, Comments, Bids, Watchlist

from itertools import chain
from operator import attrgetter

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

def index(request):
    listings = sorted(Listings.objects.all(), key=attrgetter('start_time'), reverse=True)
    return render(request, "auctions/index.html", {
        "listings": listings,
        "categories": categories,
    })

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

def comment(request, listing_id):

    comment = request.POST["comment"]

    new_comment =  Comments(
        listing=Listings.objects.get(id=listing_id),
        comment=comment,
        user=request.user,
        time=datetime.now()
        )
    new_comment.save()

    url = reverse('listing', kwargs={'listing_id': listing_id})
    return HttpResponseRedirect(url)


def bid(request, listing_id):

    bid = int(request.POST["bid"])
    listing = Listings.objects.get(id=listing_id)

    # Check bid is greater than start price / highest bid on the listing
    # Note: When listings are created, the highest_bid will be set equal to the start price
    if bid > listing.highest_bid:
        listing.highest_bid = bid
        listing.highest_bid_user = request.user

        # Saves the highest bid and associated user under that listing
        listing.save()

        # Also register the bid in bids model.
        new_bid =  Bids(
            listing=listing,
            bid=bid,
            user=request.user,
            time=datetime.now()
            )
        new_bid.save()
    else:
       message = "Your bid must be higher than the current price"
       # the 'layout.html' template displays the message
       return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': listing_id}) + f'?message={message}')

    return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': listing_id}))


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

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def profile(request):

    user_listings = Listings.objects.filter(user=request.user)
    # looks up the listings the user has bid on.
    # distinct() removes the duplicate listings if the user has bid more than once on the same listing
    bid_on_listings = Listings.objects.filter(bids__user=request.user).distinct()

    winning = []
    losing = []
    # see whether the user that placed the highest bid is the current user
    # if so, place that listing in a list they are winning
    for listing in bid_on_listings:

        # Check if the user's bid is the current winning bid
        # Note this adds both Active and In-Active Listings
        if listing.highest_bid_user == request.user:
            winning.append(listing)
        else:
            losing.append(listing)

    watchlist = Watchlist.objects.filter(user=request.user)

    return render(request, "auctions/profile.html", {
        "user_listings": user_listings,
        "winning": winning,
        "losing": losing,
        "bid_on_listings": bid_on_listings,
        "watchlist": watchlist,
        "categories": categories,
    })

def close(request, listing_id):
    if request.method == "GET":
        listing = Listings.objects.get(id=listing_id)
        comments = Comments.objects.filter(listing=listing_id)
        bids = Bids.objects.filter(listing=listing_id)
        bid_count = bids.count()

        # Mergers the data for comments and bids, then sorts by time, to give a history for the listing
        history = sorted(chain(bids, comments), key=attrgetter('time'), reverse=True)

        return render(request, "auctions/close.html", {
            "listing": listing,
            "categories": categories,
            'history': history,
            "bid_count": bid_count,
        })

    if request.method == "POST":
        listing = Listings.objects.get(id=listing_id)

        listing.end_time = datetime.now()
        listing.active = False
        listing.save()

        url = reverse('listing', kwargs={'listing_id': listing_id})
        return HttpResponseRedirect(url)


def watch(request, listing_id):
    listing = Listings.objects.get(id=listing_id)

    # Check if the user is already watching the listing
    watching = Watchlist.objects.filter(listing=listing, user=request.user)

    # Use the exists() function to see if the item is already on the watchlist
    if watching.exists():
        watching.delete()
    else:
        new_watch = Watchlist(
                listing=listing,
                user=request.user,
                time=datetime.now(),
            )
        new_watch.save()

    url = reverse('listing', kwargs={'listing_id': listing_id})
    return HttpResponseRedirect(url)


def category(request, category):
    listings = Listings.objects.filter(category=category)

    return render(request, "auctions/categories.html", {
        "listings": listings,
        "category": category,
        "categories": categories,
    })