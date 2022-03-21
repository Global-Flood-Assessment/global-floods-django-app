

def read_json():
    json = gpd.read_file('./temp_file/footprint.geojson')
    a = json.convex_hull
    response = requests.get('https://js-157-200.jetstream-cloud.org/ModelofModels/gis_output/flood_warning_'+post_date+'.zip')
    _tmp_file = tempfile.TemporaryFile()
    _tmp_file.write(response.content)
    zf = zipfile.ZipFile(_tmp_file, mode='r')
    if os.path.exists('../zip'):
        os.rmdir('../zip')
    os.mkdir('../zip')
    for names in zf.namelist():
        f = zf.extract(names, '../zip')  # 解压到zip目录文件下
    zf.close()
    os.rmdir('../zip')
    shpdata = gpd.GeoDataFrame.from_file('../zip/flood_warning_'+post_date+'.shp')
    shpdata = shpdata.loc[shpdata['pfaf_id'] == pid]
    shpdata.to_file('../shapefile/Polygon.shp',driver='ESRI Shapefile',encoding='utf-8')
    s2_classification.classification(a,post_date,dc_end)
    s2_classification.classification(a,dc_start,pre_date)
