import requests
import json
# import related models here
from .models import CarDealer, DealerReview

from requests.auth import HTTPBasicAuth

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
import requests
import json
from .models import CarDealer
from requests.auth import HTTPBasicAuth

def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

    
# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)

def post_request(url, json_payload, **kwargs): 
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data
    except:
        print("Network exception occurred")
        return "error in sentiment analyze"


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["dealerships"]
        # For each dealer object
        for dealer in dealers:
            # Create a CarDealer object 
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter   
    json_result = get_request(url, dealerId=kwargs["dealer_id"])
    if json_result:
        # Get the row list in JSON as review
        reviews = json_result["reviews"]
        # For each review object
        for review in reviews:
            # Create a DealerReviewk object 
            dealer_obj = DealerReview(dealership=review["dealership"], name=review["name"], 
                                purchase=review["purchase"],review=review["review"], purchase_date=review["purchase_date"],
                                car_make=review["car_make"], car_model=review["car_model"], car_year=review["car_year"],
  #                              sentiment=analyze_review_sentiments(review["review"]),
                                sentiment=analyze_review_sentiments(text=review["review"], version = "2022-04-07", features ="sentiment", return_analyzed_text=True),
                                id=review["id"])
            results.append(dealer_obj)

    return results



# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(**kwargs):
    params = dict()
    params["text"] = kwargs["text"]
    params["version"] = kwargs["version"]
    params["features"] = kwargs["features"]
    params["return_analyzed_text"] = kwargs["return_analyzed_text"]
    params["language"] = "en"
    
    try:
        response = requests.get("https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/c3ed412d-5d86-4df9-b6a9-d40b2b88adc2/v1/analyze?version=2021-08-01", params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', 'wgyYxvaO9ru8kEKUnGw69xeXJuVagSSOwlONPMjmRQcz'))
        return json.loads(response.text)['sentiment']['document']['label'] 
    except:
        print("Network exception occurred")
        return "error in sentiment analyze"

