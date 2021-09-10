from dash import dcc, html
from dash.dependencies import Input, Output

from app import app
from apps import overview, top
from navigation_menu import nav_menu

app.layout = html.Div(
    [
        nav_menu,

        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ],
    style=dict(margin="50px")
)

header_contents = html.Div(
    [
        html.H5('ストレングスファインダーWebAppへようこそ',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P('')
    ]
)

route_layout = html.Div(
    [
        header_contents,
    ]
)


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/':
        return route_layout
    elif pathname == '/top':
        return top.layout
    elif pathname == '/overview':
        return overview.layout
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True, port=8080, host='0.0.0.0')
