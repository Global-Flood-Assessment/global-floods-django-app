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
import os
import jinja2
import shapely

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
    map,df = pick_map()
    m = map._repr_html_()
    context = {'map': m}
    if request.method == "POST":
        if 'run-model' in request.POST:
            lat = request.COOKIES.get('lat')
            lng = request.COOKIES.get('lng')
            pfaf = df.loc[(df['Lat']==float(lat)) & (df['Lon']==float(lng))]
            if len(pfaf) >1:
                pfaf = pfaf.iloc[0]
            sim_geo = gpd.GeoSeries(pfaf['geometry_y']).simplify(tolerance=0.001)
            geo_j = sim_geo.to_json()
            s_date = request.POST.get("pre-event")
            e_date = request.POST.get("post-event")
            if s_date <= e_date:
                messages.error(request,'Please fill both pre-event and post-event date! Also please make sure pre is befor after!')
            # pred(s_date, e_date, poly=geo_j)
            return render(request, 'global_floods_django_app/pick.html',context)
        elif 'download' in request.POST:
            x = 1
    return render(request, 'global_floods_django_app/pick.html', context)

def draw(request):
    map = draw_map()
    m = map._repr_html_()
    context = {'map': m}
    if request.method == "POST":
        if 'run-model' in request.POST:
            geo_info = request.COOKIES.get('geometry')
            s_date = request.POST.get("pre-event")
            e_date = request.POST.get("post-event")
            if s_date <= e_date:
                messages.error(request,'Please fill both pre-event and post-event date! Also please make sure pre is befor after!')
            # pred(s_date, e_date, poly=geo_info)
            return render(request, 'global_floods_django_app/draw.html',context)
        elif 'download' in request.POST:
            x=1
    return render(request, 'global_floods_django_app/draw.html', context)

def upload(request):
    global poly
    context = {'map':'null'}
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TEMP_FILE = os.path.join(BASE_DIR, "global_floods_django_app", "static/temp_file", "footprint.geojson")
    if request.method == "POST":
        if 'ufile' in request.POST:
            File = request.FILES.get("myfile",None)
            if File is None:
                messages.error(request,"There is no chosen file ")
            else:
                with open(TEMP_FILE, 'wb+') as f:
                    for chunk in File.chunks():
                        f.write(chunk)
            map = show_map()
            m = map._repr_html_()
            context = {'map': m}
            return render(request, 'global_floods_django_app/upload.html', context)
        elif 'run-model' in request.POST:
            s_date = request.POST.get("pre-event")
            e_date = request.POST.get("post-event")
            if s_date <= e_date:
                messages.error(request,'Please fill both pre-event and post-event date! Also please make sure pre is befor after!')
            # pred(s_date, e_date, poly=None)
            return render(request, 'global_floods_django_app/upload.html', context)
        elif 'download' in request.POST:
            x=1
    return render(request, 'global_floods_django_app/upload.html')

def result(request):
    map = pick_map()
    m = map._repr_html_()
    context = {'map': m}
    return render(request, 'global_floods_django_app/result.html', context)
