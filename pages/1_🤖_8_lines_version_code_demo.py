"""
This is a Streamlit web app for visualizing areas impacted by rising sea level.
"""

import json
import streamlit as st
import geemap.foliumap as geemap
import ee
from streamlit_folium import folium_static

from utils import validate_gee_service_account_key

st.set_page_config(page_title="8 lines code demo", page_icon="🤖")

st.write("# Rising Sea Level impact (2050) on lands in red")

DEMO_CODE = """
ee.Initialize(ee.ServiceAccountCredentials(
    st.secrets.gee_service_account,
    key_data=st.secrets.gee_service_account_credentials))

# create map centered on hong kong with district level zoom
m = geemap.Map(center=(22.30, 114.1694), zoom=14, basemap="HYBRID")
dem = ee.Image("NASA/NASADEM_HGT/001")
impacted_land = dem.expression(
    "(elevation < 0.3) && (swb == 0)",
    {'elevation': dem.select('elevation'),
     'swb': dem.select('swb')})
#...
"""
st.code(DEMO_CODE, language="python", line_numbers=False)


def initialize_earth_engine():
    """
    Initialize the Google Earth Engine (ee) client.

    Priority:
    1. If Streamlit secrets contains 'gee_service_account' and
       'gee_service_account_credentials', attempt service account initialization.
       - 'gee_service_account' should be the service account email.
       - 'gee_service_account_credentials' can be a JSON string or dict (the
         service account key contents).
    2. Otherwise, try ee.Initialize() (useful for local development where the
       user has run `earthengine authenticate`).
    On failure, display a clear Streamlit error message and stop the app.
    """
    try:
        sa_key_name = "gee_service_account"
        sa_key_data_name = "gee_service_account_credentials"

        if sa_key_name in st.secrets and sa_key_data_name in st.secrets:
            service_account = st.secrets[sa_key_name]
            key_data = st.secrets[sa_key_data_name]

            # Validate the key_data before using it
            is_valid, err = validate_gee_service_account_key(key_data)
            if not is_valid:
                st.error("Invalid Google Earth Engine service account credentials.")
                st.write("Validation error: " + err)
                st.stop()

            # Ensure key_data is a JSON string for the EE client
            if isinstance(key_data, dict):
                key_json = json.dumps(key_data)
            else:
                key_json = str(key_data)

            creds = ee.ServiceAccountCredentials(service_account, key_data=key_json)
            ee.Initialize(creds)
        else:
            # Fall back to default initialization (for local/dev environments).
            ee.Initialize()
    except Exception as e:
        st.error("Failed to initialize Google Earth Engine (ee).")
        st.markdown(
            "Possible causes:\n"
            "- Missing or invalid Streamlit secrets `gee_service_account` and/or "
            "`gee_service_account_credentials` for service account initialization.\n"
            "- No local Earth Engine authentication (run `earthengine authenticate`).\n\n"
            "See https://developers.google.com/earth-engine/python_install for setup instructions."
        )
        st.write(f"Error details: `{e}`")
        st.stop()


# Initialize Earth Engine safely
initialize_earth_engine()

# create map centered on hong kong with district level zoom
m = geemap.Map(center=(22.30, 114.1694), zoom=14, basemap="HYBRID")
dem = ee.Image("NASA/NASADEM_HGT/001")
impacted_land = dem.expression(
    "(elevation < 0.3) && (swb == 0)",
    {'elevation': dem.select('elevation'),
     'swb': dem.select('swb')})

viz_params = {'min': 0, 'max': 1, 'palette': ['000000', 'FF0000'],
              'opacity': 0.4}

m.addLayer(impacted_land, viz_params, 'impacted areas')
m.addLayerControl()

# render folium map
folium_static(m)
"""