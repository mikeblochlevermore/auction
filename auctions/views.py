from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime
from django.db.models import Max

from .models import User, Listings, Comments, Bids

from itertools import chain
from operator import attrgetter



def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listings.objects.all(),
    })

def listing(request, listing_id):
    listing = Listings.objects.get(id=listing_id)
    comments = Comments.objects.filter(listing=listing_id)
    bids = Bids.objects.filter(listing=listing_id)

    highest_bid = bids.aggregate(Max('bid'))['bid__max']

    # Mergers the data for comments and bids, then sorts by time, to give a history for the listing
    history = sorted(chain(bids, comments), key=attrgetter('time'))

    return render(request, "auctions/listing.html", {
        "listing": listing,
        'history': history,
        "highest_bid": highest_bid,
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

    # Check the new bid is higher than the current highest bid
    bids = Bids.objects.filter(listing=listing_id)
    highest_bid = bids.aggregate(Max('bid'))['bid__max']

    # if no bids, set the highest_bid to the start price of the listing
    if highest_bid is None:
        listing = Listings.objects.get(id=listing_id)
        highest_bid = listing.start_price

    # Save the new bid if it is the highest offer
    if bid > highest_bid:

        new_bid =  Bids(
            listing=Listings.objects.get(id=listing_id),
            bid=bid,
            user=request.user,
            time=datetime.now()
            )
        new_bid.save()
    else:
        print("must be a higher amount than the current price")

    url = reverse('listing', kwargs={'listing_id': listing_id})
    return HttpResponseRedirect(url)


def new_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        image = request.POST["image"]
        start_price = request.POST["start_price"]
        category = request.POST["category"]
        end_time = request.POST["end_time"]

        new_listing = Listings(
            title=title,
            description=description,
            image=image,
            start_price=start_price,
            category=category,
            user=request.user,
            start_time=datetime.now(),
            end_time=end_time
        )

        new_listing.save()

        return render(request, "auctions/index.html", {
        "listings": Listings.objects.all(),
        })
    else:
        return render(request, "auctions/new_listing.html", {
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
