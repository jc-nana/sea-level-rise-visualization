import plotly.graph_objs as go
# from plotly.offline import iplot
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
        line=dict(color='white', width=2)  # Black line with thickness of 2
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
        # Position the legend in the upper left corner
        legend=dict(x=0.05, y=0.95),
        margin=dict(l=50, r=50, t=50, b=50),  # Set plot margins
        hovermode='closest',  # Show closest data point on hover
    )

    # Create the figure with data and layout
    fig = go.Figure(data=data_plots, layout=layout)

    # # Show the figure
    # iplot(fig)
    return fig

# Note: If you are using a Jupyter Notebook, make sure to include the following to enable Plotly offline:
# from plotly.offline import init_notebook_mode
# init_notebook_mode(connected=True)
