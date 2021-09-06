import numpy as np
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from markdown_txt import txt as markdown_txt
from app.utils import nav_menu, create_content_header

import pandas as pd


def get_layout(df_top5):
    layout = html.Div([
        nav_menu,
        create_content_header('マッチング',
                              '2つの入力ボックスに対象の方の氏名を入力してください'),
        html.P('メンティー集合を入力してください'),
        dcc.Dropdown(
            id='group_personsA',
            options=[{'label': i, 'value': i}
                     for i in np.unique(df_top5.index)],
            multi=True,
            style=dict(backgroundColor='#FFE4E1',
                       #    marginLeft='10px',
                       #   width='60%',
                       #    backgroundPaddingLeft="50px",
                       )
        ),
        html.Br(),
        html.P('メンター集合を入力してください'),
        dcc.Dropdown(
            id='group_personsB',
            options=[{'label': i, 'value': i}
                     for i in np.unique(df_top5.index)],
            multi=True,
            style=dict(backgroundColor='#E6E6FA',
                       #    marginLeft='10px',
                       #    width='60%',
                       #    paddingLeft="30px",
                       )
        ),
        html.Br(),
        html.B(id='matching_check',
                  style=dict(color='red')
               ),
        dcc.Graph(id='matching',
                  responsive=True,
                  )
    ], style=dict(margin="50px"))
    # style={'display': 'inline-block', }
    return layout
