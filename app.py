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
data, file_list = load_data()
if data:
    channels = data[file_list[0]]
    posts = data[file_list[1]]
    reactions = data[file_list[2]]
    subscribers = data[file_list[3]]
    views = data[file_list[4]]

processed_data = process_data(channels, posts, reactions, subscribers, views)

# Create the app layout
app.layout = create_layout(processed_data)

# Register callbacks
register_callbacks(app, processed_data)

if __name__ == '__main__':
    app.run_server(debug=True)

