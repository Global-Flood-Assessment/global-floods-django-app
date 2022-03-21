from django.shortcuts import render,redirect

# Create your views here.
# coding:utf-8
from django.http import HttpResponse
from django.template import loader,Context
from django.views.generic import TemplateView
from .read_MoM_point import *
import folium
import datetime
from .forms import *
from .models import *
import json
from django.contrib import messages
from django_tables2.tables import Table

s_date=''
e_date=''
poly = '1'

def index(request):
    context = {'map':'load failed'}
    map = init_map()
    m = map._repr_html_()
    context = {'map': m}
    return render(request, 'global_floods_django_app/index.html', context)

def pick(request):
    map = pick_map()
    m = map._repr_html_()
    context = {'map': m}
    return render(request, 'global_floods_django_app/pick.html', context)

def draw(request):
    form = OSmapForm()
    if request.method == "POST":
        if 'run-model' in request.POST:
            poly = request.POST.get('poly')
            context = {'alert_flag':True,'form':form,'result':True}

            return render(request, 'global_floods_django_app/draw.html',context)
    return render(request, 'global_floods_django_app/draw.html', {'form': form})

def upload(request):
    global poly
    context = {'map':'null'}
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TEMP_FILE = os.path.join(BASE_DIR, "global_floods_django_app", "temp_file", "footprint.geojson")
    if request.method == "POST":
        if 'ufile' in request.POST:
            File = request.FILES.get("myfile",None)
            if File is None:
                return HttpResponse("There is no chosen file ")
            else:
                with open(TEMP_FILE, 'wb+') as f:
                    for chunk in File.chunks():
                        f.write(chunk)
            map = show_map()
            m = map._repr_html_()
            context = {'map': m}
            return render(request, 'global_floods_django_app/upload.html', context)
        elif 'run-model' in request.POST:
            return render(request, 'global_floods_django_app/result.html',{'alert_flag': True})
    return render(request, 'global_floods_django_app/upload.html')

def result(request):
    map = pick_map()
    m = map._repr_html_()
    context = {'map': m}
    return render(request, 'global_floods_django_app/result.html', context)
