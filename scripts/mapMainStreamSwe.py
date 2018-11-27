
import pandas as pd
import folium as flm
from folium.plugins import MarkerCluster
import json


EMBED_HTML = False

style_function = lambda feature: {
        'fillColor': 'transparent',
        'color': 'black',
        'weight': 2,
        'dashArray': '5, 5'
    }


# Create map
mapMT = flm.Map(location=[47.2, -110], max_zoom=12, control_scale=False, tiles='Stamen Terrain')

# Montana Counties outline
counties_fn = r'../data/countiesMT_4326.geojson'
with open(counties_fn) as f:
    dat = json.load(f)

for feat in (dat['features']):
    name = feat['properties']['NAME']
    gj = flm.GeoJson(data=feat, overlay=True, style_function=style_function, name=name)
    gj.add_to(mapMT)

# Add streamflow stuff
pntsStream = r'../data/streamflow/MT_active_gages.geojson'

with open(pntsStream) as f:
    stmGauges = json.load(f)

sf_cluster = MarkerCluster().add_to(mapMT)

for feats in (stmGauges['features']):
    lon, lat = feats['geometry']['coordinates']
    id = feats['properties']['STAID']
    icon = flm.Icon(icon='ok', color='red')

    try:
        with open('../graphs/'+id+'.html', 'r') as f:
            html = f.read()

    except IOError:
        continue

    iframe = flm.IFrame(html=html, width=800, height=600)
    pop = flm.Popup(iframe, max_width=2500)
    mark = flm.Marker([lat, lon], icon=icon, popup=pop)
    mark.add_to(sf_cluster)

# # Add SWE Stuff
# pntsSnotel = r'../data/swecoords.json'
#
# with open(pntsSnotel) as f:
#     snotel = json.load(f)
#
# swe_cluster = MarkerCluster().add_to(mapMT)
#
# for feats in snotel:
#     lon, lat = snotel[feats]
#     id = str(feats)
#     icon = flm.Icon(icon='ok', color='blue')
#
#     try:
#         with open('../graphs/swe/'+id+'.html', 'r') as f:
#             html = f.read()
#     except IOError:
#         continue
#
#     iframe = flm.IFrame(html=html, width=800, height=600)
#     pop = flm.Popup(iframe, max_width=2500)
#     mark = flm.Marker([lat, lon], icon=icon, popup=pop)
#     mark.add_to(swe_cluster)


#Retrieve geojson
# https://waterservices.usgs.gov/nwis/dv/?format=json,1.1&sites=06090800&startDT=2005-01-01
#flm.LayerControl().add_to(mapMT)

legend_html = '''
     <div style="position: fixed; 
     bottom: 50px; left: 50px; width: 175px; height: 80px; 
     border:2px solid grey; z-index:9999; font-size:14px;
     ">&nbsp; USGS Streamflow &nbsp; <i class="fa fa-map-marker fa-2x"
                  style="color:red"></i><br>
     &nbsp; SNOTEL SWE &nbsp; <i class="fa fa-map-marker fa-2x"
                  style="color:blue"></i>
      </div>
     '''
mapMT.get_root().html.add_child(flm.Element(legend_html))

mapMT.fit_bounds(mapMT.get_bounds())
mapMT.save('../streamflowMap2.html')
