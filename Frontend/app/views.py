from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth.models import User

import requests

from dotenv import load_dotenv
import os
from app.tools.tokenizer import Tokenizer
from datetime import datetime
from base64 import b64encode
from django.contrib import messages
# Create your views here
# 192.168.85.209

load_dotenv()
API = os.environ.get("API_LINK")
tokenizer = Tokenizer()

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
            'year': datetime.now().year
        }
        return render(request, 'index.html', tparams)
    else:
        return redirect('login')

#OK
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

        token = tokenizer.gerateEmailToken(request.user.email)
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
            'numtests' : json['num_testes'],
            'registerdate': json['register_date'],
            'role': json['role'],
            'picture' : picture,
            'year': datetime.now().year
        }

        return render(request, 'user/nonAdmin/profile/profile.html', tparams)
    else:
        return redirect('login')

#OK
def editProfile(request):
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

        token = tokenizer.gerateEmailToken(request.user.email)
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
            picture = "data:image/png;base64,"+ json['picture']
        else:
            picture = os.environ.get("NO_PIC")

        tparams = {
            'name' : json['name'],
            'email': json['email'],
            'numtests' : json['num_testes'],
            'registerdate': json['register_date'],
            'role': json['role'],
            'picture' : picture,
            'year': datetime.now().year
        }

        return render(request, 'user/nonAdmin/profile/profileEdit.html', tparams)
    else:
        return redirect('login')

#API
def updateProfile(request):
    if request.user.is_authenticated:
        token = tokenizer.gerateEmailToken(request.user.email)

        try:
            name = request.POST['name']
        except:
            messages.error(request, "Profile did not update.")
            return redirect('profile')

        try:
            pic = request.FILES['picture'].file.read()
            b64pic = b64encode(pic)
            pic = b64pic.decode("utf-8")
        except:
            pic = None

        message = {'name': name, 'pic' : pic}

        r = requests.put(API + "profile", json=message, headers={'Authorization': 'Bearer '+ token})

        if r.status_code != 200:
            messages.error(request, "Profile did not update.")
        else:
            messages.info(request, "Profile updated.")
        return redirect('profile')

    else:
        return redirect('login')

#API
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
        if not request.user.is_superuser:
            token = tokenizer.userToken(request.user.email)
            r = requests.get(API + "experience", headers={'Authorization': 'Bearer '+ token})

            if r.status_code != 200:
                return HttpResponseNotFound()

            json = r.json()

            tparms = {
                'database' : json,
                'year': datetime.now().year
            }
            return render(request, 'user/nonAdmin/tests/previousTests/dashboard.html', tparms)
        else:
            return HttpResponseForbidden()
    else:
        return redirect('login')

#API
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
        if not request.user.is_superuser:
            token = tokenizer.gerateEmailToken(request.user.email)
            r = requests.get(API + "experince/" + str(testID), headers={'Authorization': 'Bearer '+ token})

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
                'register_date': str(register_date),
                'year': datetime.now().year
            }

            return render(request, 'user/nonAdmin/tests/previousTests/testInfo.html', tparms)
        else:
            return HttpResponseForbidden()
    else:
        return redirect('login')

#OK
def createUser(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return render(request, 'user/admin/newUser/addUser.html', {'picture': os.environ.get("NO_PIC")})
        else:
            return HttpResponseForbidden()
    else:
        return redirect('login')

#API
def userCreation(request):
    if request.user.is_authenticated:
        if request.user.is_superuser and request.method == "POST":
            email = request.POST['email']
            name = request.POST['name']
            role = int (request.POST['role'])
            password = hash(email)

            token = tokenizer.generateValidation(email)

            message = {'email' : email, 'name' : name, 'role' : role}

            link = 'http://localhost:8000/create/user/validate/'


            r = requests.post(API + "user/", json=message, headers={'Authorization': 'Bearer ' + token})

            if r.status_code != 200:
                return HttpResponseForbidden()


            user = User.objects.create_user(email, email, password)
            user.first_name = name
            user.save()

            newEmail = EmailMessage(
                'AMazING Playground',
                'Dear '+ name + ',\n' +
                'Your account have been created.\n' +
                'Please use the following link validate your account:\n' +
                link + token,
                os.getenv('EMAIL'),
                [email]
            )
            newEmail.send(fail_silently=False)

            messages.info(request, "User successfully created.")
            return redirect('createUser')
        else:
            return HttpResponseForbidden()
    else:
        return redirect('login')

#OK
def validateUser(request, token):
    if not request.user.is_authenticated:
        email = tokenizer.checkToken(token)

        if email == None: return HttpResponseForbidden()

        tparms = {
            'email' :  email,
            'token' : token,
            'picture' : os.getenv('NO_PIC'),
            'year': datetime.now().year
        }
        return render(request, 'user/nonAdmin/validation/validation.html', tparms)
    else:
        return redirect('home')

#OK
def saveUser(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            try:
                password = request.POST['password']
                token = request.POST['token']
            except:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

            decoded = tokenizer.checkToken(token)

            print(password)
            if decoded != None:
                user = User.objects.get(email=decoded)
                user.set_password(password)
                user.save()
                return redirect('login')
            else:
                return HttpResponseForbidden()
        else:
            return redirect('login')
    else:
        return redirect('home')

#OK
def rankUp(request):
    if request.user.is_authenticated:
        newEmail = EmailMessage(
            'AMazING Playground - Rank up',
            'Dear Admin,\n' +
            'The user' + request.user.email + ' requested a rank up to his account.',
            os.getenv('EMAIL'),
            [request.user.email, os.getenv('EMAIL_ADMIN')]
        )
        newEmail.send(fail_silently=False)
        messages.info(request, "Request sent.")
        return redirect('profile')
    else:
        return redirect('login')

#TODO
def listUsers(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            token = tokenizer.gerateEmailToken(request.user.email)
            r = requests.get(API + "user",  headers={'Authorization': 'Bearer '+ token})

            if r.status_code != 200:
                return HttpResponseNotFound()

            json = r.json()

            tparms = {
                'year': datetime.now().year,
                'database' : json
            }
            return render(request, 'user/admin/listUsers/list/allUsers.html', tparms)

        else:
            return HttpResponseForbidden()
    else:
        return redirect('login')

#API
def searchUser(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:

            try:
                content = request.POST['content']
                typeID = request.POST['type']
            except:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

            token = tokenizer.gerateEmailToken(request.user.email)

            if typeID != "" and content != "":
                message = {'type': typeID, 'content': content}

                r = requests.get(API + "user?typeID=" + typeID + "&content=" + content, json=message, headers={'Authorization': 'Bearer ' + token})

                if r.status_code != 200:
                    messages.error(request, "Something went wrong.")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

                json = r.json()

                return render(request, "user/admin/listUsers/list/allUsers.html", {'year': datetime.now().year, 'database': json})

            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        else:
            return HttpResponseForbidden()
    else:
        return redirect('login')

#OK
def editUser(request, userId):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            token = tokenizer.gerateEmailToken(request.user.email)
            r = requests.get(API + "user/" + str(userId), headers={'Authorization': 'Bearer ' + token})

            if r.status_code != 200:
                return HttpResponseNotFound()

            json = r.json()

            if json['picture'] != None:
                picture = json['picture']
            else:
                picture = os.environ.get("NO_PIC")

            tparams = {
                'year': datetime.now().year,
                'userID' : json['id'],
                'name': json['name'],
                'email': json['email'],
                'role': json['role'],
                'picture': picture
            }

            return render(request, "user/admin/listUsers/edit/editRole.html", tparams)
        else:
            return HttpResponseForbidden()
    else:
        return redirect('login')

#API
def processUser(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            token = tokenizer.gerateEmailToken(request.user.email)

            try:
                email = request.GET['email']
                userID = request.GET['id']
            except:
                messages.error(request, "Something went wrong.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


            if email != "" and userID != "":
                message = {'email' : email, 'id' : userID}
                r = requests.put(API + "user/" + str(userID), json=message, headers={'Authorization': 'Bearer ' + token})

                if r.status_code != 200:
                    messages.error(request, "Something went wrong.")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

                messages.info(request, "User updated.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            else:
                messages.error(request, "Something went wrong.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            return HttpResponseForbidden()
    else:
        return redirect('login')

#API
def networkStatus(request):
    if request.user.is_authenticated:
        return render(request, 'network/status.html', {'year': datetime.now().year,})
    else:
        return redirect('login')
#API
def processNode(request, nodeID):
    if request.user.is_authenticated:
        token = tokenizer.nodeToken(request.user.email)
        r = requests.get(API + "node/" + str(nodeID), headers={'Authorization': 'Bearer ' + token})

        if r.status_code != 200:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        json = r.json()

        password = b64encode(b'amazing')

        tparms = {
            'current_time' : str(datetime.now()),
            'year': datetime.now().year,
            'id' : json['id'],
            'ips' : json['ips'],
            'mac' : json['mac'],
            'placas' : json['placas'],
            'state' : json['state'],
            'username' : 'amazing',
            'password' : password.decode("utf-8")
        }

        return render(request, "network/nodeInfo.html", tparms)
    else:
        return redirect('login')

#API
def searchTest(request):
    if request.user.is_authenticated:
        if not request.user.is_superuser:

            try:
                content = request.POST['content']
                typeID = request.POST['type']
            except:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

            token = tokenizer.gerateEmailToken(request.user.email)

            if typeID != "" and content != "":
                message = {'type': typeID, 'content': content}

                r = requests.get(API + "experience?typeID=" + typeID + "&content=" + content , json=message, headers={'Authorization': 'Bearer ' + token})

                if r.status_code != 200:
                    messages.error(request, "Something went wrong.")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

                json = r.json()

                return render(request, "user/nonAdmin/tests/previousTests/dashboard.html", {'year': datetime.now().year, 'database': json})

            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        else:
            return HttpResponseForbidden()
    else:
        return redirect('login')


def calendar(request):
    if request.user.is_authenticated:
        return render(request, 'calendar/calendar.html')
    else:
        return redirect('login')

def registerTest(request):
    if request.user.is_authenticated:
        return render(request, 'calendar/registerTest.html')
    else:
        return redirect('login')