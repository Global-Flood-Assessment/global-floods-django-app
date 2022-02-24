from django.shortcuts import render

# Create your views here.
# coding:utf-8
from django.http import HttpResponse
from django.template import loader,Context
from django.views.generic import TemplateView
from MainPage.read_MoM_point import *
import folium
import datetime

s_date=''
e_date=''

def index(request):
    context = {'map':'load failed'}
    map = init_map()
    m = map._repr_html_()
    context = {'map': m}
    return render(request, 'index.html', context)

def pick(request):
    context = {'map':'load failed'}
    if request.method == "POST":
        print('xxx')
        if 'area' in request.POST:
            print('xxx')
            value = request.POST.get("myInput", None)
            res = value.split('Alert level')[0]
            res = int(res)
            map = pick_map(res)
            m = map._repr_html_()
    else:
        map = pick_map()
        m = map._repr_html_()
        context = {'map': m}
    return render(request, 'pick.html', context)

def draw(request):
    context = {'map':'load failed'}
    map = draw_map()
    m = map._repr_html_()
    context = {'map': m}
    return render(request, 'draw.html', context)

def upload(request):
    context = {'map':'null'}
    if request.method == "POST":
        if 'ufile' in request.POST:
            File = request.FILES.get("myfile", None)
            if File is None:
                return HttpResponse("There is no chosen file ")
            else:
                with open("./temp_file/footprint.geojson", 'wb+') as f:
                    for chunk in  File.chunks():
                        f.write(chunk)
            map = show_map()
            m = map._repr_html_()
            context = {'map': m}
            return render(request, 'upload.html', context)
        elif 'run' in request.POST:
            s_date = request.POST.get("pre-event")
            e_date = request.POST.get("post-event")
            s_date = s_date.replace('-','')
            e_date = e_date.replace('-','')
            return render(request, 'result.html')
    return render(request, 'upload.html')

def result(request):
    context = {'map':'Processing'}
    if request.method == "POST":
        if 'no' in request.POST:
            return render(request, 'index.html')
        else:
            s_date = request.POST.get("pre-event")
            e_date = request.POST.get("post-event")
            s_date = s_date.replace('-','')
            e_date = e_date.replace('-','')
            map = pred()
            m = map._repr_html_()
            context = {'map': m}
    return render(request, 'result.html', context)
