from dash import dcc, html
from dash.dependencies import Input, Output

from app import app
from apps import (custom_error, data_delete, data_edit, download, list,
                  matching, overview, person, qa, team, top, upload,
                  upload_result)
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


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/':
        return top.layout
    elif pathname == '/list':
        return list.layout
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
