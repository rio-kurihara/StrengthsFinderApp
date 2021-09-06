import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from markdown_txt import txt as markdown_txt
from app.utils import nav_menu, create_content_header


def get_layout():
    layout = html.Div([
        nav_menu,
        create_content_header('各機能のアルゴリズム詳細',
                              ''),
        html.P('作成中'),
        create_content_header('問い合わせ先',
                              ' '),

    ],
        style=dict(margin='50px')
    )
    return layout
