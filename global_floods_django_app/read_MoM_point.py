import requests
from bs4 import BeautifulSoup
import csv
import urllib
import pandas as pd
import geopandas as gpd
import datetime
import cv2
import numpy as np
import json
import zipfile
import tempfile
import os
from geopy.geocoders import Nominatim
import folium
import folium.plugins as plugins
#from .S2_classification import *
#from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt

def init_map():
    colors = {1:'green', 2:'orange', 3:'red'}
    # get all csv files
    url = 'https://js-157-200.jetstream-cloud.org/ModelofModels/glofas/'
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    links = soup.find_all('a')
    geojson_file_list = []
    for link in links:
        a = link.get("href")
        if '.geojson' in a:
            geojson_file_list.append(url+a)
    geojson_file_list.reverse()
    m = folium.Map()
    df = gpd.read_file(geojson_file_list[0])
    df = df.loc[df['Alert_level'] >= 1]
    tooltip = 'click to see details for this event'
    for i in range(len(df)):
        row = df.iloc[i,:]
        Longitude = str(row['Lon'])
        Latitude = str(row['Lat'])
        add = 'Location: '+str(row['Basin'])+', '+ str(row['Country_code'])
        alert_level = 'Alert level: ' + str(row['Alert_level'])+'\n'
        text = alert_level + add
        folium.Marker([row['Lat'],row['Lon']], popup=text, tooltip=tooltip, icon=folium.Icon(color=colors[row['Alert_level']])).add_to(m)
    return m

def pick_map():
    m = plugins.DualMap()
    colors = {1:'green', 2:'orange', 3:'red'}
    # get all csv files
    url = 'https://js-157-200.jetstream-cloud.org/ModelofModels/glofas/'
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    links = soup.find_all('a')
    geojson_file_list = []
    for link in links:
        a = link.get("href")
        if '.geojson' in a:
            geojson_file_list.append(url+a)
    geojson_file_list.reverse()
    geo_link = geojson_file_list[0].replace('/glofas/','/gis_output/')
    geo_link = geo_link.replace('threspoints_','flood_warning_')
    geo_link = geo_link.replace('00.geojson','.geojson')
    df = gpd.read_file(geojson_file_list[-1])
    df = df.loc[df['Alert_level'] >= 1]
    tooltip = 'click to see details for this event'
    for i in range(len(df)):
        row = df.iloc[i,:]
        Longitude = str(row['Lon'])
        Latitude = str(row['Lat'])
        add = 'Location: '+str(row['Basin'])+', '+ str(row['Country_code'])
        alert_level = 'Alert level: ' + str(row['Alert_level'])+'\n'
        text = alert_level + add
        folium.Marker([row['Lat'],row['Lon']], popup=text, tooltip=tooltip, icon=folium.Icon(color=colors[row['Alert_level']])).add_to(m.m1)
    folium.GeoJson(geo_link, zoom_on_click=True).add_to(m.m2)
    return m

def show_map():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TEMP_FILE = os.path.join(BASE_DIR, "global_floods_django_app", "temp_file", "footprint.geojson")
    m = folium.Map()
    folium.GeoJson(TEMP_FILE, tooltip='Your uploaded area', zoom_on_click=True).add_to(m)
    return m

def pred(request, poly=None):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TEMP_FILE = os.path.join(BASE_DIR, "global_floods_django_app", "temp_file", "footprint.geojson")
    s_date = request.POST.get("pre-event")
    e_date = request.POST.get("post-event")
    s_date = s_date.replace('-','')
    e_date = e_date.replace('-','')
    if poly is None:
        poly = geojson_to_wkt(read_geojson(TEMP_FILE))
    classification(poly,(0,100),s_date,e_date)
    return 0
