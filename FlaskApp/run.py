import dash_html_components as html
from app import app
from navigation_menu import nav_menu


header_contents = html.Div(
    [
        html.H5('ストレングスファインダーWebAppへようこそ',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P('')
    ]
)


app.layout = html.Div(
    [
        nav_menu,
        header_contents
    ],
    style=dict(margin="50px")
)


if __name__ == '__main__':
    app.run_server(debug=True, port=8080, host='0.0.0.0')
