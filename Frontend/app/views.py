from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
import requests

from dotenv import load_dotenv
import os
from app.tools.tokenizer import Tokenizer
from datetime import datetime

# Create your views here
# 192.168.85.209

load_dotenv()

API = os.environ.get("API_LINK")
genToken = Tokenizer()


def home(request):
    """
    Homepage view.
    Args:
        request: request data;

    Returns:
        If the user is logged in
        homepage rendered, otherwise,
        returns login page.
    """
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

        token = genToken.gerateEmailToken(request.user.email)
        r = requests.get(API + "profile", headers = {'Authorization': 'Bearer '+ token})

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

        if json['picture'] != None:
            picture = json['picture']
        else:
            picture = os.environ.get("NO_PIC")

        tparams = {
            'name' : json['name'],
            'email': json['email'],
            'numtests' : json['numtests'],
            'registerdate': json['registerdate'],
            'role': json['role'],
            'picture' : picture
        }

        return render(request, 'user/profile.html', tparams)
    else:
        return redirect('login')

def checkTests(request):
    """
    Show tests done by logged user.
    Args:
        request: request data;

    Returns:
        When status code is 200, display
        user tests page, otherwise
        404 page.
    """
    if request.user.is_authenticated:
        token = genToken.gerateEmailToken(request.user.email)
        r = requests.get(API + "tests", headers={'Authorization': 'Bearer '+ token})

        if r.status_code != 200:
            return HttpResponseNotFound()

        json = r.json()

        tparms = {
            'database' : json,
        }
        return render(request, 'tests/dashboard.html', tparms)
    else:
        return redirect('login')

def checkTestInfo(request, testID):
    """
    Show info for a specific test.
    Args:
        request: request data;
        testID: test id to search;

    Returns:
        When status code is 200, display
        show specific test page, otherwise
        404 page.
    """
    if request.user.is_authenticated:
        token = genToken.gerateEmailToken(request.user.email)
        r = requests.get(API + "tests/" + str(testID), headers={'Authorization': 'Bearer '+ token})

        if r.status_code != 200:
            return HttpResponseNotFound()

        json = r.json()

        register_date = datetime.fromtimestamp(json['register_date'])
        begin_date = datetime.fromtimestamp(json['begin_date'])
        end_date = datetime.fromtimestamp(json['end_date'])

        tparms = {
            'begin_date': str(begin_date),
            'end_date': str(end_date),
            'num_test': json['num_test'],
            'template': json['template'],
            'name': json['name'],
            'register_date': str(register_date)
        }

        return render(request, 'tests/testInfo.html', tparms)
    else:
        return redirect('login')