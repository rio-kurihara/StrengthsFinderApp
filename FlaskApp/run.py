import dash_core_components as dcc
import dash_html_components as html
from app import app

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


if __name__ == '__main__':
    app.run_server(debug=True, port=8080, host='0.0.0.0')
