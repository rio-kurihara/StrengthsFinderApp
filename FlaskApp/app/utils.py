from flask import Flask
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html

nav_menu = dbc.Nav(
    [
        dbc.NavLink("Top",
                    href="/top/",
                    external_link=True),
        dbc.NavLink("OverView",
                    href="/dashboard/overview",
                    external_link=True),
        dbc.DropdownMenu(
            [
                dbc.NavLink("Group",
                            href="/dashboard/group",
                            external_link=True),
                dbc.NavLink("Person",
                            href="/dashboard/person",
                            external_link=True),
                dbc.NavLink("Matching",
                            href="/dashboard/matching",
                            external_link=True),
            ],
            label="DashBoard",
            nav=True
        ),
        dbc.DropdownMenu(
            [
                dbc.NavLink("Download",
                            href="/download",
                            external_link=True),
                dbc.NavLink("Upload",
                            href="/upload",
                            external_link=True),
                dbc.NavLink("Edit",
                            href="/edit",
                            external_link=True,
                            disabled=True),
            ],
            label="Data",
            nav=True
        ),
        dbc.NavLink("Help",
                    href="/help",
                    external_link=True
                    ),

    ],
    style=dict(margin="30px 0px"),
)


def create_content_header(title, description):
    content_header = html.Div([html.H5(title,
                                       style=dict(padding="10px",
                                                  borderLeft="5px #b31b1b solid"
                                                  )
                                       ),
                               html.P(description)
                               ])
    return content_header


def create_app(server, url_base_pathname):
    app = dash.Dash(__name__,
                    server=server,
                    url_base_pathname=url_base_pathname,
                    external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.config['suppress_callback_exceptions'] = True
    return app
