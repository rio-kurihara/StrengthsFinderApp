import numpy as np
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from markdown_txt import txt as markdown_txt
from app.utils import nav_menu, create_content_header
import pandas as pd
import numpy as np

import os
import sys

from decimal import Decimal, ROUND_HALF_UP


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


def extract_series(df, name):
    s = df[name]
    return pd.Series(s.index.values, s.values)


def merge_series(df, name_list):
    series_list = [extract_series(df, name) for name in name_list]
    return pd.concat(series_list, axis=1)


def compute_prominent_attribute(series, df):
    diff = df.add(-series, axis=0)
    diff_other_top = -series.add(-df.min(axis=1), axis=0)
    return diff.sum(axis=1).add(diff_other_top).sort_values()


def extract_only_strength(df, target_name, member_name_list, top_n=2):
    extracted_member_df = merge_series(df, member_name_list) + 1
    extracted_target_series = extract_series(df, target_name) + 1
    computed_prominent = pd.concat([compute_prominent_attribute(
        extracted_target_series, extracted_member_df), extracted_target_series, extracted_member_df.mean(axis=1)], axis=1, sort=False)

    #computed_prominent = pd.concat([computed_prominent, extracted_member_df.mean(axis=1)], axis=1)
    top_n_prominent = computed_prominent.tail(top_n)
    return top_n_prominent.index.values[::-1], top_n_prominent[1].values[::-1], top_n_prominent[2].values[::-1]


def main(df, target_name, member_name_list, top_n=2):
    # target_name = "氏名1"
    # member_name_list = ['氏名1', '氏名2', ...]

    member_name_list.remove(target_name)
    strength, target_rank, member_average_rank = extract_only_strength(
        df, target_name, member_name_list, top_n)

    member_average_rank = [int(Decimal(str(x)).quantize(
        Decimal('0'), rounding=ROUND_HALF_UP)) for x in member_average_rank]
    dict_result = {'strengths': strength,
                   'target_rank': target_rank,
                   'member_avg_rank': member_average_rank
                   }
    """
    出力例
    ['公平性' '調和性']  計算で得られた強み上位top_n個
    [9 3]                targetの人の資質順位
    [31.         24.66666667]　member_name_listの人の平均資質順位
    """
    return dict_result


def list2markdown(list_message):
    """
    資質の説明message(リスト形式)をマークダウンに変換
    """
    list_message = ['・' + x for x in list_message]
    str_message = '  \n '.join(list_message)
    return str_message


def create_maerkdown_text(dict_strengths_message, dict_result, index_num, target_name):
    strengths_name = dict_result['strengths'][index_num]
    list_message = dict_strengths_message[strengths_name]['長所']
    strengths_message = list2markdown(list_message)
    strengths_mean = dict_result['member_avg_rank'][index_num]
    target_rank = dict_result['target_rank'][index_num]

    text = """
    #### {0}
    
    {1}  
    ***
    このグループ内の{0}の平均順位は**{2}位**、  
    {3}さんの順位は**{4}位**です。

    """.format(strengths_name, strengths_message, strengths_mean, target_name, target_rank)
    return text

