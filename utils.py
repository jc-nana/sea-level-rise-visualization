"""
Contains functions for creating interactive plots of sea level rise data.
"""

import json
from typing import Tuple

import plotly.graph_objs as go
import pandas as pd


def create_sea_level_interactive_plot():
    """
    Creates an interactive plot of sea level rise data using Plotly.

    Parameters:
    - data: A pandas DataFrame with columns 'year_fraction', 'GMSL', and 'GMSL_smoothed'.
    """

    data = pd.read_csv('data/sea_level_data.csv')

    # Create the scatter plot for GMSL Variation
    gmsl_variation = go.Scatter(
        x=data['year_fraction'],
        y=data['GMSL'],
        mode='lines',
        name='GMSL Variation',
        # fill='tozeroy',  # Fill to the x-axis
        # Light blue fill with transparency
        fillcolor='rgba(135, 206, 250, 0.1)',
    )

    # Create the scatter plot for Smoothed GMSL
    smoothed_gmsl = go.Scatter(
        x=data['year_fraction'],
        y=data['GMSL_smoothed'],
        mode='lines',
        name='Smoothed GMSL',
        line=dict(color='white', width=2)  # White line with thickness of 2
    )

    # Highlight the last point with a red dot
    last_point = data.iloc[-1]
    red_dot = go.Scatter(
        x=[last_point['year_fraction']],
        y=[last_point['GMSL_smoothed']],
        mode='markers',
        marker=dict(color='red', size=10),  # Red dot with size 10
        name='2023 Level',
        showlegend=False
    )

    # Combine the plots
    data_plots = [gmsl_variation, smoothed_gmsl, red_dot]

    # Define the layout of the plot
    layout = go.Layout(
        template="plotly_dark",
        title={'text': 'Sea Level Rise Over Time',
               'x': 0.5, 'xanchor': 'center'},
        xaxis=dict(title='Year'),
        yaxis=dict(title='GMSL Variation (mm)'),
        legend=dict(x=0.05, y=0.95),
        margin=dict(l=50, r=50, t=50, b=50),  # Set plot margins
        hovermode='closest',  # Show closest data point on hover
    )

    # Create the figure with data and layout
    fig = go.Figure(data=data_plots, layout=layout)

    return fig


# --- New helper: validate GEE service account key ---
def validate_gee_service_account_key(key_data) -> Tuple[bool, str]:
    """
    Validates a Google service account key JSON.

    Accepts either:
    - a dict (parsed JSON), or
    - a JSON string.

    Returns:
    - (True, "") if valid,
    - (False, "<error message>") if invalid.

    The function checks that the JSON contains required fields for a
    service account key and that the "type" is "service_account".
    """
    try:
        if isinstance(key_data, dict):
            data = key_data
        elif isinstance(key_data, str):
            data = json.loads(key_data)
        else:
            return False, "Service account credentials must be a dict or a JSON string."
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON for service account credentials: {e}"

    required_fields = {"type", "project_id", "private_key_id", "private_key", "client_email", "client_id"}
    missing = sorted(required_fields - set(data.keys()))
    if missing:
        return False, "Missing required fields in service account JSON: " + ", ".join(missing)

    if data.get("type") != "service_account":
        return False, "The JSON 'type' field is not 'service_account'."

    # Basic sanity for private_key
    if not isinstance(data.get("private_key"), str) or "-----BEGIN PRIVATE KEY-----" not in data.get("private_key"):
        return False, "Invalid or missing 'private_key' in service account JSON."

    return True, ""


def initialize_earth_engine(st_module):
    """
    Initialize Google Earth Engine with validation and error handling.

    Args:
        st_module: The streamlit module (passed to avoid circular imports)
    """
    import ee

    try:
        sa_key_name = "gee_service_account"
        sa_key_data_name = "gee_service_account_credentials"

        if sa_key_name in st_module.secrets and sa_key_data_name in st_module.secrets:
            service_account = st_module.secrets[sa_key_name]
            key_data = st_module.secrets[sa_key_data_name]

            is_valid, err = validate_gee_service_account_key(key_data)
            if not is_valid:
                st_module.error("Invalid Google Earth Engine service account credentials.")
                st_module.write("Validation error: " + err)
                st_module.stop()

            if isinstance(key_data, dict):
                key_json = json.dumps(key_data)
            else:
                key_json = str(key_data)

            creds = ee.ServiceAccountCredentials(service_account, key_data=key_json)
            ee.Initialize(creds)
        else:
            ee.Initialize()
    except Exception as e:
        st_module.error("Failed to initialize Google Earth Engine (ee).")
        st_module.markdown(
            "Possible causes:\n"
            "- Missing or invalid Streamlit secrets `gee_service_account` and/or "
            "`gee_service_account_credentials` for service account initialization.\n"
            "- No local Earth Engine authentication (run `earthengine authenticate`).\n\n"
            "See https://developers.google.com/earth-engine/python_install for setup instructions."
        )
        st_module.write(f"Error details: `{e}`")
        st_module.stop()
