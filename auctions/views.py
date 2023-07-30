from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime, timedelta

from .models import User, Listings, Comments



def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listings.objects.all(),
    })

def listing(request, listing_id):
    listing = Listings.objects.get(id=listing_id)
    comments = Comments.objects.filter(listing=listing_id)

    if request.method == "GET":
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "comments": comments,
        })

    if request.method == "POST":
        comment = request.POST["comment"]

        new_comment =  Comments(listing=Listings.objects.get(id=listing_id), comment=comment, user=request.user, time=datetime.now())
        new_comment.save()

        return render(request, "auctions/listing.html", {
            "listing": listing,
            "comments": comments,
        })

def new_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        image = request.POST["image"]
        start_bid = request.POST["start_bid"]
        category = request.POST["category"]

        new_listing = Listings(title=title, description=description, image=image, start_bid=start_bid, category=category)
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
