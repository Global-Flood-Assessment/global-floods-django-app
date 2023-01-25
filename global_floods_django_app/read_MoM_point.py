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
import sys
import folium.plugins as plugins
from django.conf import settings
from .s2_classification import *
# from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
import jinja2

def init_map():
    colors = {1:'green', 2:'orange', 3:'red'}
    # get all csv files
    url = 'https://mom.tg-ear190027.projects.jetstream-cloud.org/ModelofModels/GLOFAS/'
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

def id2geojson_code(idlist_csv, source_mom, alert, idfield="pfaf_id"):
    """
    convert idlist in csv to geojson
    """
    if source_mom:
        "idlist_csv shall be datestr"
        adate = idlist_csv
        csvfile = download_mom(adate)
    else:
        csvfile = idlist_csv

    # load csv file
    df = pd.read_csv(csvfile, encoding="ISO-8859-1")
    # force id as int
    df[idfield] = df[idfield].astype(int)
    # drop duplicates
    df = df.drop_duplicates(subset=[idfield])

    # 1: "Information", 2: "Advisory", 3: "Watch", 4: "Warning"
    if alert:
        alist = ["Warning", "Watch"]
    else:
        alist = [""]
    pwd = os.path.dirname(__file__)
    watersheds_gdb = os.path.join(pwd,"static/temp_file/Watershed_pfaf_id.shp")
    # watersheds_gdb = "static/temp_file/Watershed_pfaf_id.shp"
    watersheds = gpd.read_file(watersheds_gdb)
    watersheds.set_index("pfaf_id", inplace=True)
    for acond in alist:
        if acond == "":
            n_df = df
        else:
            n_df = df[df.Alert == acond]
        out_df = watersheds.loc[n_df[idfield]]
        out_df = out_df.merge(n_df, left_on=idfield, right_on=idfield)
        # write warning result to geojson
        outputfile = pwd+"/static/temp_file/pick_geojson.geojson"
        # outputfile = "static/temp_file/pick_geojson.geojson"
        out_df.to_file(outputfile, index=False, driver="GeoJSON")
    return outputfile

def pick_map():
    m = plugins.DualMap()
    # Modify Marker template to include the onClick event
    click_template = """{% macro script(this, kwargs) %}
        var {{ this.get_name() }} = L.marker(
            {{ this.location|tojson }},
            {{ this.options|tojson }},
        ).addTo({{ this._parent.get_name() }}).on('click', onClick);
    {% endmacro %}"""

    # Change template to custom template
    folium.Marker._template = jinja2.Template(click_template)
    # Create the onClick listener function as a branca element and add to the map html
    click_js = """function onClick(e) {
                     var lat = e.latlng.lat;
                     var lng = e.latlng.lng;
                     document.cookie = 'lat='+lat;
                     document.cookie = 'lng='+lng;
                     }"""
    e = folium.Element(click_js)
    html = m.get_root()
    html.script.get_root().render()
    html.script._children[e.get_name()] = e
    colors = {1:'green', 2:'orange', 3:'red'}
    # get all csv files
    url = 'https://mom.tg-ear190027.projects.jetstream-cloud.org/ModelofModels/GLOFAS/'
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    links = soup.find_all('a')
    geojson_file_list = []
    for link in links:
        a = link.get("href")
        if '.geojson' in a:
            geojson_file_list.append(url+a)
    geojson_file_list.reverse()
    geo_link = geojson_file_list[0].replace('/GLOFAS/','/Final_Alert/')
    geo_link = geo_link.replace('threspoints_','Final_Attributes_')
    geo_link = geo_link.replace('00.geojson','00HWRF+MOM+DFO+VIIRSUpdated_PDC.csv')
    df = gpd.read_file(geojson_file_list[0])
    df = df.loc[(df['Alert_level'] >= 1)&(df['Basin']!='-')&(df['Country_code']!='-')]
    tooltip = 'click to see details for this event'
    outputfile=id2geojson_code(geo_link,0, 1, idfield="pfaf_id")
    df_shp = gpd.read_file(outputfile)
    df = pd.merge(df, df_shp, how='inner', on=['pfaf_id'])
    picked_id = []
    last_id = -1
    for i in range(len(df)):
        row = df.iloc[i,:]
        Longitude = str(row['Lon'])
        Latitude = str(row['Lat'])
        add = 'Location: '+str(row['Basin'])+', '+ str(row['Country_code'])
        alert_level = 'Alert level: ' + str(row['Alert_level_x'])+'\n'
        text = alert_level + add
        folium.Marker([row['Lat'],row['Lon']], popup=text, tooltip=tooltip, icon=folium.Icon(color=colors[row['Alert_level_x']])).add_to(m.m1)
    folium.GeoJson(outputfile, zoom_on_click=True).add_to(m.m2)
    return m,df

def draw_map():
    m = folium.Map()
    pwd = os.path.dirname(__file__)
    temp_draw = pwd+"/static/temp_file/temp_file.geojson"
    plugins.Draw().add_to(m)
    el = folium.MacroElement().add_to(m)
    el._template = jinja2.Template("""
            {% macro script(this, kwargs) %}

            {{ this._parent.get_name() }}.on(L.Draw.Event.CREATED, function(e){

                var layer = e.layer,
                type = e.layerType;

               //insert here your code
                console.log('type: ' + type);
                var coords_json = layer.toGeoJSON();
                console.log('coordinates: ' + coords_json['geometry']['coordinates']);
                coords_json = JSON.stringify(coords_json);
                console.log('json type: ' + coords_json);
                document.cookie = 'geometry='+coords_json;
            });

            {% endmacro %}
    """)
    return m

def show_map():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TEMP_FILE = os.path.join(BASE_DIR, "global_floods_django_app", "static/temp_file", "footprint.geojson")
    m = folium.Map()
    folium.GeoJson(TEMP_FILE, tooltip='Your uploaded area', zoom_on_click=True).add_to(m)
    return m

def pred(s_date, e_date, poly=None):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TEMP_FILE = os.path.join(BASE_DIR, "global_floods_django_app", "static/temp_file", "footprint.geojson")
    s_date = s_date.replace('-','')
    e_date = e_date.replace('-','')
    if poly is None:
        poly = geojson_to_wkt(read_geojson(TEMP_FILE))
    classification(poly,(0,100),s_date,e_date)
    return 0
