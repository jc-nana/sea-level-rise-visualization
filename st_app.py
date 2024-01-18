"""
This is a Streamlit web app for visualizing areas impacted by rising sea level.
"""

import streamlit as st
import geemap.foliumap as geemap
import ee
from streamlit_folium import folium_static
from utils import create_sea_level_interactive_plot

st.write("# Rising Sea Level impact (2050) on lands in red")

ee.Initialize(ee.ServiceAccountCredentials(
    st.secrets.gee_service_account,
    key_data=st.secrets.gee_service_account_credentials))

rise = st.slider("sea level rise (m)", 0.2, 5., value=0.3)

# create map centered on maldives capital with street level zoom
m = geemap.Map(center=(22.30, 114.1694), zoom=14, basemap="HYBRID")
dem = ee.Image("NASA/NASADEM_HGT/001")
impacted_land = dem.expression(
    f"(elevation < {rise}) && (swb == 0)",
    {'elevation': dem.select('elevation'),
     'swb': dem.select('swb')})
viz_params = {'min': 0, 'max': 1, 'palette': ['000000', 'FF0000'],
              'opacity': 0.4}

m.addLayer(impacted_land, viz_params, 'impacted areas')
m.addLayerControl()

# render folium map
folium_static(m)


st.plotly_chart(create_sea_level_interactive_plot(), use_container_width=True)

st.write(
    "#### Sea level data retrieved from [Global mean sea level](https://sealevel.nasa.gov/understanding-sea-level/key-indicators/global-mean-sea-level)")
st.write(
    "#### For more accurate sea level rise projections, visit [NASA Sea Level Projection Tool](https://sealevel.nasa.gov/ipcc-ar6-sea-level-projection-tool)")
