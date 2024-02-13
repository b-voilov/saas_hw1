import datetime as dt
import json
import os

import requests
from flask import Flask, jsonify, request

# create your API token, and set it up in Postman collection as part of the Body section
API_TOKEN = os.environ['API_TOKEN'] 
# you can get API keys for free here - https://api-ninjas.com/api/jokes
WEATHER_API_TOKEN = os.environ['WEATHER_API_TOKEN'] 

app = Flask(__name__)



def fetch_weather_data(token, location, date):
    base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
    url = f"{base_url}{location}/{date}/{date}?unitGroup=metric&key={token}"
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch data", "status_code": response.status_code}


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: python Saas.</h2></p>"


@app.route(
    "/content/api/v1/integration/generate",
    methods=["POST"],
)
def joke_endpoint():
    start_dt = dt.datetime.now()
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)
    weather = fetch_weather_data(WEATHER_API_TOKEN,json_data.get("location"),json_data.get("date"))


    result = {
        "timestamp": start_dt.isoformat(),
        "requester_name": json_data.get("requester_name"),
        "location": json_data.get("location"),
        "weather": weather,
    }

    return result