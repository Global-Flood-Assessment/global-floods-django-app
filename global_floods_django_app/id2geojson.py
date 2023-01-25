"""
    id2geojson.py
        -- watershed_id in csv file to geojson
"""
import csv
import json
import os
import sys

import geopandas as gpd
import pandas as pd


def download_mom(adate):
    """download mom output"""

    fAlert = "Final_Attributes_{}HWRF+MOM+DFO+VIIRSUpdated_PDC.csv".format(adate)
    baseurl = "https://mom.tg-ear190027.projects.jetstream-cloud.org/ModelofModels/Final_Alert/"
    dataurl = os.path.join(baseurl, fAlert)
    wgetcmd = "wget " + dataurl
    os.system(wgetcmd)

    return fAlert


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

    print(csvfile)
    # load csv file
    df = pd.read_csv(csvfile, encoding="ISO-8859-1")
    # force id as int
    df[idfield] = df[idfield].astype(int)
    # drop duplicates
    df = df.drop_duplicates(subset=[idfield])
    print(df.head())

    # 1: "Information", 2: "Advisory", 3: "Watch", 4: "Warning"
    if alert:
        alist = ["Warning", "Watch"]
    else:
        alist = [""]

    watersheds_gdb = "temp_file/Watershed_pfaf_id.shp"
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
        outputfile = idlist_csv.split(".")[0] + f"_{acond}.geojson"
        out_df.to_file(outputfile, index=False, driver="GeoJSON")

    return
