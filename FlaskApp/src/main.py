from dash import dcc, html
from dash.dependencies import Input, Output

from app import app
from apps import (auth, custom_error, data_delete, download, data_edit, matching,
                  overview, person, qa, team, top, upload, upload_result)
from navigation_menu import nav_menu

server = app.server


app.layout = html.Div(
    [
        nav_menu,
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ],
    style=dict(margin="50px")
)


welcome_message = html.H5(
    'ストレングスファインダーWebAppへようこそ',
    style=dict(padding="10px", borderLeft="5px #b31b1b solid")
)

header_contents = html.Div(
    [
        welcome_message,
        html.Br()
    ]
)

route_layout = html.Div(
    [
        header_contents,
    ]
)


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
@auth.check_ip
def display_page(pathname):
    if pathname == '/':
        return route_layout
    elif pathname == '/top':
        return top.layout
    elif pathname == '/overview':
        return overview.layout
    elif pathname == '/dashboard/person':
        return person.layout
    elif pathname == '/dashboard/team':
        return team.layout
    elif pathname == '/dashboard/matching':
        return matching.layout
    elif pathname == '/data/upload':
        return upload.layout
    elif pathname == '/data/upload_result':
        return upload_result.layout
    elif pathname == '/data/download':
        return download.layout
    elif pathname == '/data/edit':
        return data_edit.layout
    elif pathname == '/data/delete':
        return data_delete.layout
    elif pathname == '/QA':
        return qa.layout
    else:
        return custom_error.layout_404


if __name__ == '__main__':
    app.run_server(debug=True, port=8080, host='0.0.0.0')
