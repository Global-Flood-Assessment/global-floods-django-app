from django.contrib.gis import forms
from leaflet.forms.widgets import LeafletWidget




class OSmapForm(forms.Form):
    poly = forms.PolygonField(widget =
        forms.OSMWidget(attrs = {'map_width': 1024, 'map_height': 600}))
