import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from layouts import create_layout
from callbacks import register_callbacks
from data_processing import load_data, process_data

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # Expose the server variable for Gunicorn

# Load and process data
channels, posts, reactions, subscribers, views = load_data()
processed_data = process_data(channels, posts, reactions, subscribers, views)

# Create the app layout
app.layout = create_layout(processed_data)

# Register callbacks
register_callbacks(app, processed_data)

if __name__ == '__main__':
    app.run_server(debug=True)

