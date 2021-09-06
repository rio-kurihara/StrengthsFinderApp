import numpy as np
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from markdown_txt import txt as markdown_txt
from app.utils import nav_menu, create_content_header


def calc_score(df_top5, person_name: str):
    sr_agr_score = df_top5.loc[person_name].groupby('category')['score'].sum()
    dict_score = sr_agr_score.to_dict()

    return dict_score


def create_trace(list_category, dict_score: dict, person_name: str):
    # TOP5に存在しない資質カテゴリはスコアを0にする
    for _categry in list_category:
        if not _categry in dict_score:
            dict_score[_categry] = 0

    dict_score = dict(sorted(dict_score.items()))
    trace = go.Scatterpolar(
        r=list(dict_score.values()),
        theta=list(dict_score.keys()),
        fill='toself',
        name=person_name,
        opacity=0.9,
        marker=dict(
            symbol="square",
            size=8
        ),
    )

    return trace


def get_layout(df_top5):
    group_text = markdown_txt.get_group_content()
    # md_text = dcc.Markdown(group_text)

    card_content_lack_strengths1 = [
        dbc.CardBody(
            [
                dcc.Markdown(className="card-text",
                             id='lack_strengths_1')
            ]
        ),
    ]
    card_content_lack_strengths2 = [
        dbc.CardBody(
            [
                dcc.Markdown(className="card-text",
                             id='lack_strengths_2')
            ]
        ),
    ]
    card_content_unique_strengths1 = [
        dbc.CardBody(
            [
                dcc.Markdown(className="card-text",
                             id='unique_strengths_1')
            ]
        ),
    ]
    card_content_unique_strengths2 = [
        dbc.CardBody(
            [
                dcc.Markdown(className="card-text",
                             id='unique_strengths_2')
            ]
        ),
    ]

    layout = html.Div([
        nav_menu,
        create_content_header('グループの傾向把握',
                              '※参照したい方の氏名を入力してください（複数入力）'),
        dcc.Dropdown(
            id='group_persons',
            options=[{'label': i, 'value': i}
                     for i in np.unique(df_top5.index)],
            multi=True
        ),
        # グループの傾向表示
        dcc.Graph(id='my-graph'),

        # グループ内で不足している資質表示
        create_content_header('グループ内に不足している強み',
                              ''),
        dbc.Row(
            [
                dbc.Col(dbc.Card(card_content_lack_strengths1, color="danger",
                                 outline=True), width=4),
                dbc.Col(dbc.Card(card_content_lack_strengths2, color="danger",
                                 outline=True), width=4),
            ],
            className="mb-4"
            # className="mt-auto"
        ),

        # グループ内のユニークな資質表示
        create_content_header('グループ内における個人のユニークな強み',
                              '強みを知りたい人を選択してください'),
        dcc.RadioItems(id='person_drop_down'),
        dcc.Markdown(id='target_name'),
        dbc.Row(
            [
                dbc.Col(dbc.Card(card_content_unique_strengths1, color="primary",
                                 outline=True), width=4),
                dbc.Col(dbc.Card(card_content_unique_strengths2, color="primary",
                                 outline=True), width=4)
            ],
            className="mb-4",

        ),
    ], style=dict(margin="50px"))
    return layout
