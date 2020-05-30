from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth.models import User
import requests
import logging


logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(name)-12s %(levelname)-8s %(message)s'
        },
        'file': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'filename': 'info.log'
        },
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'filename': 'debug.log'
        }
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['console', 'file']
        },
        'debug': {
            'level': 'DEBUG',
            'handlers': ['console', 'debug']
        }
    }
})

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
logger = logging.getLogger(__name__)
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


# OK
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
        r = requests.get(API + "profile", headers={'Authorization': 'Bearer ' + token})
        if r.status_code != 200:
            logger.info("WRONG API STATUS CODE: " + str(r.status_code))
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
            picture = "data:image/png;base64," + json['picture']
        else:
            picture = os.environ.get("NO_PIC")

        tparams = {
            'name': json['name'],
            'email': json['email'],
            'numtests': json['num_test'],
            'registerdate': json['register_date'],
            'role': json['role'],
            'picture': picture,
            'year': datetime.now().year
        }

        return render(request, 'user/generic/profile/profile.html', tparams)
    else:
        return redirect('login')


# OK
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
        r = requests.get(API + "profile", headers={'Authorization': 'Bearer ' + token})

        if r.status_code != 200:
            logger.info("STATUS CODE: " + str(r.status_code))
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
            print(json['picture'])
            picture = "data:image/png;base64," + json['picture']
        else:
            picture = os.environ.get("NO_PIC")

        tparams = {
            'name': json['name'],
            'email': json['email'],
            'numtests': json['num_test'],
            'registerdate': json['register_date'],
            'role': json['role'],
            'picture': picture,
            'year': datetime.now().year
        }

        return render(request, 'user/generic/profile/profileEdit.html', tparams)
    else:
        return redirect('login')


# API
def updateProfile(request):
    if request.user.is_authenticated:
        token = tokenizer.gerateEmailToken(request.user.email)

        try:
            name = request.POST['name']
        except Exception as e:
            messages.error(request, "Profile did not update.")
            logger.debug("NO NAME: " + e)
            return redirect('profile')

        try:
            pic = request.FILES['picture'].file.read()
            b64pic = b64encode(pic)
            pic = b64pic.decode("utf-8")
        except Exception as e:
            logger.debug("PIC: " + str(e))
            pic = None

        message = {'name': name, 'pic': pic}

        r = requests.put(API + "profile", json=message, headers={'Authorization': 'Bearer ' + token})

        if r.status_code != 202:
            messages.error(request, "Profile did not update.")
            logger.info("STATUS CODE: " + str(r.status_code))
        else:
            messages.info(request, "Profile updated.")
        return redirect('profile')

    else:
        return redirect('login')


# API
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
            r = requests.get(API + "experience", headers={'Authorization': 'Bearer ' + token})

            if r.status_code != 200:
                return HttpResponseNotFound()

            json = r.json()

            tparms = {
                'database': json,
                'year': datetime.now().year
            }
            return render(request, 'user/nonAdmin/tests/previousTests/dashboard.html', tparms)
        else:
            return HttpResponseForbidden()
    else:
        return redirect('login')


# API
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
            token = tokenizer.userToken(request.user.email)
            r = requests.get(API + "experience/" + str(testID), headers={'Authorization': 'Bearer ' + token})

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


# OK
def createUser(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return render(request, 'user/admin/newUser/addUser.html', {'picture': os.environ.get("NO_PIC")})
        else:
            return HttpResponseForbidden()
    else:
        return redirect('login')


# API
def userCreation(request):
    if request.user.is_authenticated:
        if request.user.is_superuser and request.method == "POST":
            email = request.POST['email']
            name = request.POST['name']
            role = int(request.POST['role'])
            password = hash(email)

            token = tokenizer.gerateEmailToken(email)

            message = {'email': email, 'name': name, 'role': role}
            link = 'http://192.168.85.209:8005/create/user/validate/'

            r = requests.post(API + "user", json=message, headers={'Authorization': 'Bearer ' + token})

            if r.status_code != 201:
                return HttpResponseForbidden()

            user = User.objects.create_user(email, email, password)
            user.first_name = name
            user.save()

            newEmail = EmailMessage(
                'AMazING Playground',
                'Dear ' + name + ',\n' +
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


# OK
def validateUser(request, token):
    if not request.user.is_authenticated:
        email = tokenizer.checkToken(token)
        if email == None: return HttpResponseForbidden()

        tparms = {
            'email': email,
            'token': token,
            'picture': os.getenv('NO_PIC'),
            'year': datetime.now().year
        }
        return render(request, 'user/nonAdmin/validation/validation.html', tparms)
    else:
        return redirect('home')


# OK
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


# OK
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


# TODO
def listUsers(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            token = tokenizer.gerateEmailToken(request.user.email)
            r = requests.get(API + "user", headers={'Authorization': 'Bearer ' + token})

            if r.status_code != 200:
                return HttpResponseNotFound()

            json = r.json()

            tparms = {
                'year': datetime.now().year,
                'database': json,
                'nopic' : os.environ.get("NO_PIC")
            }

            logger.info(json)
            return render(request, 'user/admin/listUsers/list/allUsers.html', tparms)

        else:
            return HttpResponseForbidden()
    else:
        return redirect('login')


# API
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
                if typeID == "0": r = requests.get(API + "user?email=" + content,
                                 headers={'Authorization': 'Bearer ' + token})
                else: r = requests.get(API + "user?content=" + content,
                                 headers={'Authorization': 'Bearer ' + token})

                if r.status_code != 200:
                    messages.error(request, "Something went wrong.")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

                print(r.text)

                json = r.json()

                print(json)

                return render(request, "user/admin/listUsers/list/allUsers.html",
                              {'year': datetime.now().year, 'database': json})

            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        else:
            return HttpResponseForbidden()
    else:
        return redirect('login')


# OK
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
                'userID': json['id'],
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


# API
def processUser(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            token = tokenizer.gerateEmailToken(request.user.email)

            try:
                email = request.GET['email']
                userID = request.GET['id']
                role = request.POST['role']
            except:
                messages.error(request, "Something went wrong.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

            if email != "" and userID != "":
                message = {'email': email, 'id': userID, 'role': role}
                r = requests.put(API + "user/" + str(userID), json=message,
                                 headers={'Authorization': 'Bearer ' + token})

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


# API
def networkStatus(request):
    if request.user.is_authenticated:
        return render(request, 'network/status.html', {'year': datetime.now().year, })
    else:
        return redirect('login')


# API
def processNode(request, nodeID):
    if request.user.is_authenticated:
        token = tokenizer.nodeToken(request.user.email)
        r = requests.get(API + "node/" + str(nodeID), headers={'Authorization': 'Bearer ' + token})


        if r.status_code != 200:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        json = r.json()

        token = tokenizer.gerateEmailToken(request.user.email)
        r = requests.get(API + "profile", headers={'Authorization': 'Bearer ' + token})
        if r.status_code != 200:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        role = r.json()

        token = tokenizer.nodeToken(request.user.email)
        r = requests.get(API + "experience/now", headers={'Authorization': 'Bearer ' + token})
        if r.status_code != 200:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        ongoing = r.json()

        ongoing = ongoing['current_experience']

        password = b64encode(b'amazing')

        hostname = json['hostname']
        interfaces = json['interfaces']

        lista = []
        lista2 = []
        dic = {}
        dic2 = {}
        for i in interfaces:
            if interfaces[i]['logic_state'] != "DOWN":
                if interfaces[i]['ip'] != None:
                    dic['name'] = i
                    dic['end'] = interfaces[i]['addrs']
                    dic['ip']= interfaces[i]['ip']
                    dic['mac'] = interfaces[i]['mac']
                    dic['logic_state'] = interfaces[i]['logic_state']
                    lista.append(dic)
                else:
                    dic['name'] = i
                    dic['end'] = [{'addr': '-', 'broadcast': '-', 'netmask': '-', 'peer': '-'}]
                    dic['ip'] = '127.0.0.1'
                    dic['mac'] = interfaces[i]['mac']
                    dic['logic_state'] = interfaces[i]['logic_state']
                    lista.append(dic)
                dic = {}
            else:
                dic2['name'] = i
                dic2['mac'] = interfaces[i]['mac']
                lista2.append(dic2)
                dic2 = {}
        try:
            uEmail = ongoing['email']
        except:
            uEmail = None

        if request.user.is_superuser or uEmail == request.user.email:
            access = 1
        else:
            access = 0

        isAdmin = 0
        if request.user.is_superuser: isAdmin = 1

        tparms = {
            'current_time': str(datetime.now()),
            'year': datetime.now().year,
            'role': role['role'],
            'isAdmin' : isAdmin,
            'access' : access,
            'database' : lista,
            'database2' : lista2,
            'hostname': hostname,
            'username': 'amazing',
            'password': password.decode("utf-8"),
            'nodeID' : nodeID
        }

        return render(request, "network/nodeInfo.html", tparms)
    else:
        return redirect('login')


# API
def searchTest(request):
    if request.user.is_authenticated:
        if not request.user.is_superuser:

            try:
                content = request.POST['content']
                typeID = request.POST['type']
            except:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

            token = tokenizer.gerateEmailToken(request.user.email)

            print(typeID, content)

            if typeID != "" and content != "":
                if typeID == "0": r = requests.get(API + "experience?begin_date=" + content,
                                 headers={'Authorization': 'Bearer ' + token})
                else: r = requests.get(API + "experience?content=" + content,
                                 headers={'Authorization': 'Bearer ' + token})
               

                if r.status_code != 200:
                    messages.error(request, "Something went wrong.")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

                json = r.json()

                return render(request, "user/nonAdmin/tests/previousTests/dashboard.html",
                              {'year': datetime.now().year, 'database': json})

            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        else:
            return HttpResponseForbidden()
    else:
        return redirect('login')

# API
def checkTestsAdmin(request):
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
        if request.user.is_superuser:
            token = tokenizer.gerateEmailToken(request.user.email)
            r = requests.get(API + "experience", headers={'Authorization': 'Bearer ' + token})

            if r.status_code != 200:
                return HttpResponseNotFound()

            json = r.json()

            tparms = {
                'database': json,
                'year': datetime.now().year
            }
            return render(request, 'user/admin/experiences/dashboard.html', tparms)
        else:
            return HttpResponseForbidden()
    else:
        return redirect('login')


# API
def checkTestInfoAdmin(request, testID):
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
        if request.user.is_superuser:
            token = tokenizer.gerateEmailToken(request.user.email)
            r = requests.get(API + "experience/" + str(testID), headers={'Authorization': 'Bearer ' + token})

            if r.status_code != 200:
                print(r.status_code)
                return HttpResponseNotFound()

            json = r.json()

            experience = json['experience']
            config_list = json['config_list']
            print(config_list)
            tparms = {
                'author' : json['author'],
                'begin_date': experience['begin_date'],
                'end_date': experience['end_date'],
                'register_date': experience['register_date'],
                'name': experience['name'],
                'status' : experience['status'],
                'configs' : config_list,
                'testID' : testID,
                'year': datetime.now().year
            }

            return render(request, 'user/admin/experiences/testeInfo.html', tparms)
        else:
            return HttpResponseForbidden()
    else:
        return redirect('login')


def searchTestAdmin(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:

            try:
                content = request.POST['content']
                typeID = request.POST['type']
            except:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

            token = tokenizer.gerateEmailToken(request.user.email)

            if typeID != "" and content != "":
                if typeID == "0": r = requests.get(API + "experience?begin_date=" + content,
                                 headers={'Authorization': 'Bearer ' + token})
                else: r = requests.get(API + "experience?content=" + content,
                                 headers={'Authorization': 'Bearer ' + token})

                if r.status_code != 200:
                    messages.error(request, "Something went wrong.")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

                json = r.json()

                return render(request, "user/admin/experiences/dashboard.html",
                              {'year': datetime.now().year, 'database': json})

            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        else:
            return HttpResponseForbidden()
    else:
        return redirect('login')

def createAcessPoint(request, nodeID):
    if request.user.is_authenticated:
        token = tokenizer.nodeToken(request.user.email)
        r = requests.get(API + "experience/now", headers={'Authorization': 'Bearer ' + token})
        if r.status_code != 200:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        ongoing = r.json()

        ongoing = ongoing['current_experience']

        try:
            uEmail = ongoing['email']
        except:
            uEmail = None

        if request.user.is_superuser or uEmail == request.user.email:
            access = 1
        else:
            access = 0

        if access == 0:
            return HttpResponseForbidden("No access")

        return render(request, "network/create/AP.html", {'year': datetime.now().year, 'nodeID':nodeID})

    else:
        return redirect('login')

def processAP(request, nodeID):
    if request.user.is_authenticated:
        token = tokenizer.nodeToken(request.user.email)
        r = requests.get(API + "experience/now", headers={'Authorization': 'Bearer ' + token})
        if r.status_code != 200:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        ongoing = r.json()

        ongoing = ongoing['current_experience']

        try:
            uEmail = ongoing['email']
        except:
            uEmail = None

        if request.user.is_superuser or uEmail == request.user.email:
            access = 1
        else:
            access = 0

        if access == 0:
            return HttpResponseForbidden("No access")

        try:
            APPW = request.POST['APPW']
        except:
            APPW = None

        try:
            APSSID = request.POST['APSSID']
            Channel = request.POST['Channel']
            RangeStart = request.POST['RangeStart']
            RangeEnd = request.POST['RangeEnd']
            hw_mode = request.POST['hw_mode']
            DFGateway = request.POST['DFGateway']
            Netmask = request.POST['Netmask']
        except Exception as e:
            print(e)
            return redirect('networkstatus')
        msg = {
            'APSSID' : APSSID,
            'APPW': APPW,
            'Channel' : Channel,
            'RangeStart' : RangeStart,
            'RangeEnd' : RangeEnd,
            'hw_mode' : hw_mode,
            'DFGateway' : DFGateway,
            'Netmask': Netmask
        }
        r = requests.post(API + "node/" + str(nodeID) + "/accesspoint", json=msg)

        if r.status_code != 200:
            print(r.status_code)
            messages.error(request, "Something went wrong.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        return redirect('networkstatus')
    else:
        return redirect('login')


def registerTest(request):
    if request.user.is_authenticated:
        
        token = tokenizer.simpleToken(request.user.email)
        r = requests.get(API + 'template', headers={'Authorization': 'Bearer ' + token})

        if r.status_code != 200:
            print(r.status_code)
            logging.debug("API ERROR: " + str(r.status_code))
            messages.error(request, "Something went wrong.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        
        json = r.json()

        lista = []

        for i in json:
            lista.append(i['template']['id'])
        
        lista.sort()

        return render(request, 'calendar/registerTest.html', {'database':lista, 'year': datetime.now().year })
    else:
        return redirect('login')

def registerTestSave(request):
    if request.user.is_authenticated:
        try:
            name = request.POST['name']
            begin_date = request.POST['begin_date']
            end_date = request.POST['end_date']
            template = int(request.POST['template'])
            num_test = int(request.POST['num_test'])
        except Exception as e:
            logging.debug("Parsing exception: " + e)
            messages.error(request, "Something went wrong.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        
        begin_date = begin_date.split("T")[0] + " " + begin_date.split("T")[1] + ":00"
        end_date = end_date.split("T")[0] + " " + end_date.split("T")[1] + ":00"

        msg = {'name' : name, 'begin_date' : begin_date, 'end_date' : end_date, 'template' : template, 'num_test' : num_test}

        token = tokenizer.simpleToken(request.user.email)
        r = requests.post(API + "experience", json=msg, headers={'Authorization': 'Bearer ' + token})

        if r.status_code != 201:
            print(r.status_code)
            logging.debug("API CODE ERROR: " + str(r.status_code))
            messages.error(request, "Something went wrong.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        messages.info(request, "Test booked up")
        return redirect('calendar')

    else:
        return redirect('login')

def calendar(request):
    if request.user.is_authenticated:

        token = tokenizer.gerateEmailToken(request.user.email)

        r = requests.get(API + "experience", headers={'Authorization': 'Bearer ' + token})

        if r.status_code != 200:
            messages.error(request, 'Something went wrong')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        test_info = r.json()

        tests = []

        for test in test_info:
            t_id = test['id']
            name = test['author'] + ' - ' + test['name']
            data = test['begin_date']
            tests.append({'name': name, 'date': data, 'id': str(t_id), 'type': 'event'})

        return render(request, 'calendar/calendar.html', {'database': tests, 'year': datetime.now().year})
    else:
        return redirect('login')

def listTemplates(request):
    if request.user.is_authenticated:

        token = tokenizer.simpleToken(request.user.email)
        r = requests.get(API + "template", headers={'Authorization': 'Bearer ' + token})

        if r.status_code != 200:
            print(r.status_code)
            messages.error(request, 'Something went wrong')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        
        json = r.json()

        tparms = {
            'database' : json
        }

        return render(request, 'network/templates/listTemplates.html', tparms)

    else:
        return redirect('login')


def templateInfo(request, templateID):
    if request.user.is_authenticated:

        token = tokenizer.simpleToken(request.user.email)
        r = requests.get(API + "template/" + str(templateID), headers={'Authorization': 'Bearer ' + token})

        if r.status_code != 200:
            messages.error(request, 'Something went wrong')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        json = r.json()

        tparms = {
            'author' : json['author'],
            'config_list' : json['config_list'],
            'template' : json['template']
        }

        return render(request, 'network/templates/templateInfo.html', tparms)

    else:
        return redirect('login')

def interfaceUP(request, node, iName):
    if request.user.is_authenticated:
        token = tokenizer.simpleToken(request.user.email)
        r = requests.get(API + "node/" + str(node) + "/" + str(iName) + "/up", headers={'Authorization': 'Bearer ' + token})

        if r.status_code != 200:
            json = r.json()
            messages.error(request, json['msg'])
            return redirect('nodestatus', nodeID=node)

        json = r.json()
        messages.info(request, json['msg'])
        return redirect('nodestatus', nodeID=node)
    else:
        return redirect('login')

def interfaceDown(request, node, iName):
    if request.user.is_authenticated:
        token = tokenizer.simpleToken(request.user.email)
        r = requests.get(API + "node/" + str(node) + "/" + str(iName)  + "/down", headers={'Authorization': 'Bearer ' + token})

        if r.status_code != 200:
            json = r.json()
            messages.error(request, json['msg'])
            return redirect('nodestatus', nodeID=node)

        json = r.json()
        messages.info(request, json['msg'])
        return redirect('nodestatus', nodeID=node)
    else:
        return redirect('login')

def openFileTest(request, file, testID):
    if request.user.is_authenticated:
        token = tokenizer.userToken(request.user.email)
        r = requests.get(API + "experience/" + str(testID), headers={'Authorization': 'Bearer ' + token})

        if r.status_code != 200:
            return HttpResponseNotFound()

        json = r.json()

        json=json['config_list']

        for i in json:
            if i['experience'] == file:
                val = i['file']
                break;

        return render(request, 'user/admin/experiences/openfile.html', {'file' : val})

    else:
        return redirect('login')


def iperfServer(request, nodeID):
    if request.user.is_authenticated:
        return render(request, 'network/create/iperfServer.html', {'year': datetime.now().year, 'nodeID': nodeID})
    else:
        return redirect('login')


def iperfClient(request, nodeID):
    if request.user.is_authenticated:
        return render(request, 'network/create/iperfClient.html', {'year': datetime.now().year, 'nodeID': nodeID})
    else:
        return redirect('login')


def processIpServer(request, nodeID):
    if request.user.is_authenticated:
        '''
        token = tokenizer.nodeToken(request.user.email)
        r = requests.get(API + "", headers={'Authorization': 'Bearer ' + token}) # preencher se necessario
        if r.status_code != 200:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '')) # preencher se necessario
        '''
        try:
            time = request.POST['time']
        except:
            time = 0

        try:
            protocol = request.POST['protocol']
        except:
            protocol = 'tcp'

        try:
            mtu = request.POST['mtu']
        except Exception as e:
            print(e)
            return redirect('networkstatus')

        msg = {
            'protocol': protocol,
            'time': time,
            'mtu': mtu
        }
        r = requests.post(API + "" + str(nodeID) + "", json=msg)

        if r.status_code != 200:
            print(r.status_code)
            messages.error(request, "Something went wrong.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        return redirect('networkstatus')
    else:
        return redirect('login')


def processIpClient(request, nodeID):
    if request.user.is_authenticated:
        '''
        token = tokenizer.nodeToken(request.user.email)
        r = requests.get(API + "", headers={'Authorization': 'Bearer ' + token})
        if r.status_code != 200:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        '''

        try:
            time = request.POST['time']
        except:
            time = 0

        try:
            protocol = request.POST['protocol']
        except:
            protocol = 'tcp'

        try:
            bandwidth = request.POST['bandwidth']
            mtu = request.POST['mtu']
        except Exception as e:
            print(e)
            return redirect('networkstatus')

        msg = {
            'protocol': protocol,
            'time': time,
            'bandwidth': bandwidth,
            'mtu': mtu
        }
        r = requests.post(API + "" + str(nodeID) + "", json=msg)

        if r.status_code != 200:
            print(r.status_code)
            messages.error(request, "Something went wrong.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        return redirect('networkstatus')
    else:
        return redirect('login')


def userStatistics(request):
    if request.user.is_authenticated:
        return render(request, 'statistics/admin.html', {'year': datetime.now().year})
    else:
        return redirect('login')

def adminStatistics(request):
    if request.user.is_authenticated:
        return render(request, 'statistics/user.html', {'year': datetime.now().year})
    else:
        return redirect('login')