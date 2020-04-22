from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from datetime import datetime, timedelta, timezone
import jwt
# Create your views here
# 192.168.85.209
from datetime import datetime
import requests
from datetime import datetime, timedelta, timezone

from jwt import (
    JWT,
    jwk_from_pem,
)
from jwt.utils import get_int_from_datetime
from dotenv import load_dotenv
import os
load_dotenv()

API = os.environ.get("API_LINK")

jwtManager = JWT()
with open("app/certificates/privateKey.pem", 'rb') as reader:
    input_key = jwk_from_pem(reader.read())

def home(request):
    if request.user.is_authenticated:
        tparams = {
            'title': 'Home Page',
            'year': datetime.now().year,
        }
        return render(request, 'index.html', tparams)
    else:
        return redirect('login')

def profile(request):
    """
    User profile view.
    Args:
        request: request data;

    Returns:
        When status code is 200, display
        user profile page, otherwise
        404 page.

    """
    if request.user.is_authenticated:

        message = {
            'email': request.user.email,
            'iat': get_int_from_datetime(datetime.now(timezone.utc)),
            'exp': get_int_from_datetime(
                datetime.now(timezone.utc) + timedelta(minutes=1)),
        }

        token = jwtManager.encode(message, input_key, alg='RS256')
        r = requests.get(API + "profile", headers = {'Authorization': token})

        if r.status_code != 200:
            return HttpResponseNotFound()

        json = r.json()
        """
        Example of expected reponse:
            {
                email: "ruicoelho@ua.pt",
                id: 200,
                name: "Rui",
                numtests: 130,
                picture: null,
                registerdate: "03-05-2019",
                role: 1
            }
        """
        tparams = {
            'name' : json['name'],
            'email': json['email'],
            'numtests' : json['numtests'],
            'registerdate': json['registerdate'],
            'role': json['role']
        }
        print(tparams)

    else:
        return redirect('login')