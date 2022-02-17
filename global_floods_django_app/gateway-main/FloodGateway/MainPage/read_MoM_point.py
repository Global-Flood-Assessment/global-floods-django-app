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
        folium.Marker([row['Lon'],row['Lat']], popup=text, tooltip=tooltip, icon=folium.Icon(color=colors[row['Alert_level']])).add_to(m)
    return m

def draw_map():
    m = folium.Map()
    d_opt = {'polyline': {'allowIntersection': False}}
    e_opt={'poly': {'allowIntersection': False}}
    s = plugins.Draw(export=True,filename='./temp_file/footprint.geojson', draw_options=d_opt, edit_options=e_opt).add_to(m)
    print(s)
    return m

def pick_map(res = None):
    colors = {1:'green', 2:'orange', 3:'red'}
    # get all csv files
    url = 'https://js-157-200.jetstream-cloud.org/ModelofModels/gis_output/'
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    links = soup.find_all('a')
    geojson_file_list = []
    for link in links:
        a = link.get("href")
        if '.geojson' in a:
            geojson_file_list.append(url+a)
    geojson_file_list.reverse()
    m = plugins.Map()
    df = gpd.read_file(geojson_file_list[-1])
    folium.GeoJson(geojson_file_list[-1], zoom_on_click=True, ).add_to(m)
    tooltip = 'click to see details for this event'
    for i in range(len(df)):
        row = df.iloc[i,:]
        Longitude = str(row['Lon'])
        Latitude = str(row['Lat'])
        add = 'Location: '+str(row['Basin'])+', '+ str(row['Country_code'])
        alert_level = 'Alert level: ' + str(row['Alert_level'])+'\n'
        value = str(row['pfaf_id'])+'\n'+alert_level + add
        text = f'<input type="text" disabled="disabled" value={value} name="myInput"><br><input name="area" type="submit" value="See more details">'
        folium.Marker([row['Lon'],row['Lat']], popup=text, tooltip=tooltip, icon=folium.Icon(color=colors[row['Alert_level']])).add_to(m.m1)
        if res is not None:
            a = geojson_file_list[-1].replace('glofas/threspoints','gis_output/flood_warning')
            a=a.replace('00.geojson','.geojson')
            geojson = gpd.read_file(a)
            geojson = geojson.loc[geojson['pfaf_id'] == res]
            with open("./temp_file/footprint.geojson", 'wb+') as f:
                f.write(geojson.to_json())
            folium.GeoJson(geojson.to_json(), zoom_on_click=True).add_to(m.m2)
    return m

def show_map():
    m = folium.Map()
    folium.GeoJson('./temp_file/footprint.geojson', tooltip='Your uploaded area', zoom_on_click=True).add_to(m)
    return m

def pred():
    return 0
