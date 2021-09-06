import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from markdown_txt import txt as markdown_txt
from app.utils import nav_menu, create_content_header


def get_plot_table_data(df, dict_colors_strengths, dict_strengths_desc, list_person):
    data = []

    for i in range(1, 35):
        x = list(df[df['rank'] == i].loc[list_person]['strengths'])
        x_rpl = [_x.replace(_x, 'コミュニ<br>ケ―ション') if _x ==
                 'コミュニケーション' else _x for _x in x]
        trace = go.Bar(
            x=list_person,
            y=[1 for _ in list_person],
            marker=dict(color=[dict_colors_strengths[_x] for _x in x],
                        line=dict(
                color='rgb(8,48,107)',
                width=1.5,
            )
            ),
            hoverinfo='text',
            hovertext=[dict_strengths_desc[_x] for _x in x],
            text=x_rpl,
            textposition='inside',

        )
        data.append(trace)
    return data


def get_layout(list_person):
    layout = html.Div([
        nav_menu,
        create_content_header('受診済みの方の資質ランキング表示',
                              '参照したい方の氏名を入力してください（複数可）'),
        dcc.Dropdown(
            id='input_id',
            options=[{'label': i, 'value': i} for i in list_person],
            multi=True,
        ),
        dcc.Graph(id='my-graph'),
    ],
        style=dict(margin='50px')
    )
    return layout
