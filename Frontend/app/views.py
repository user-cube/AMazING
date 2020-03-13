from django.shortcuts import render, redirect

# Create your views here.
from datetime import datetime

def home(request):
    if request.user.is_authenticated:
        tparams = {
            'title': 'Home Page',
            'year': datetime.now().year,
        }
        return render(request, 'index.html', tparams)
    else:
        return redirect('login')
