from dash import Dash

def init_dashboard(server):
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dashapp/'
    )

    dash_app.layout = html.Div(id='dash-container')

    return dash_app.server

def init_callbacks(dash_app):
    @app.callback()

    