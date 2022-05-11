
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarModel

# from .restapis import related methods
from .restapis import get_request, get_dealers_from_cf, get_dealer_reviews_from_cf,post_request

from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import uuid

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)



# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)


# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/user_login.html', context)
    else:
        return render(request, 'djangoapp/user_login.html', context)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/user_registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/user_registration.html', context)


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://f9727b38.eu-gb.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context = {"dealership_list": dealerships}
        return render(request, 'djangoapp/index.html', context)


#def dealer_details(request,Dealer name, Dealer_ID):
#           detail={"name":Dealer name,”id”=Dealer_ID}
#                return render(request, 'dealer_details.html', detail)

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_name, dealer_id):
    if request.method == "GET":
        url = "https://f9727b38.eu-gb.apigw.appdomain.cloud/api/review"
        # Get dealers from the URL
        reviews = get_dealer_reviews_from_cf(url, dealer_id=dealer_id)
        context = {"review_list": reviews, "dealer_name": dealer_name, "dealer_id": dealer_id}
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_name, dealer_id):    
    if request.method == "GET":
        cars = CarModel.objects.all()
        context = {}
        context["cars"] = cars
        context["dealer_name"] = dealer_name
        context["dealer_id"] = dealer_id
        print(context)
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == "POST":
        if request.user.is_authenticated:
            review = {}
            review["time"] = datetime.utcnow().isoformat()
            review["name"] = request.user.username
            review["dealership"] = dealer_id
            review["review"] = request.POST.get("content")
            review["purchase"] = "true" if request.POST.get("purchasecheck")== "on" else "false"
            car = CarModel.objects.get(pk=request.POST.get("car"))
            review["purchase_date"] = request.POST.get("purchasedate")
            review["car_make"] = car.carMake.name
            review["car_model"] = car.carModelType
            review["car_year"] = car.year.strftime("%Y")
            review["id"] = uuid.uuid4().hex[:5].upper()
            json_payload = {"review": review}
            response = post_request("https://f9727b38.eu-gb.apigw.appdomain.cloud/api/review", json_payload, dealerId=dealer_id)
            return redirect("djangoapp:dealer_details", dealer_name=dealer_name, dealer_id=dealer_id)
        else:
            return HttpResponse("User is not logged")
