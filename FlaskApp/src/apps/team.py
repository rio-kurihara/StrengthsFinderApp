import json
import os
import sys
from decimal import ROUND_HALF_UP, Decimal

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import yaml
from dash import dcc, html
from dash.dependencies import Input, Output

from app import app


# ------------------------------------------------------------------------------
# データ読み込み
# ------------------------------------------------------------------------------

# settings
with open('settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

base_dir = config['base_dir']

mst_category_path = base_dir + config['mst_category_path']
mst_message_json_path = base_dir + config['mst_message_json_path']
strengths_path = base_dir + config['strengths_path']
top5_path = base_dir + config['top5_path']
all34_path = base_dir + config['all34_path']
all34_exsits_null_path = base_dir + config['all34_exsits_null_path']


# load data
df_mst = pd.read_csv(mst_category_path)
df_strength_org = pd.read_csv(strengths_path)
df_top5 = pd.read_csv(top5_path, index_col='index')
df_all = pd.read_csv(all34_exsits_null_path, index_col='index')
df_all = df_all.fillna('nan')
dict_strengths_message = pd.read_json(mst_message_json_path)


list_category = df_mst['category'].unique()
dict_strengths_category = df_mst.set_index('strengths')['category'].to_dict()

# ------------------------------------------------------------------------------
# 機能1 グループの傾向把握: callbackの設定
# ------------------------------------------------------------------------------


def calc_score(df_top5, user_name: str):
    """ TODO

    Args:
        df_top5 (pd.DataFrame): 全ユーザーの資質ランキング
        user_name (str): ユーザー名

    Returns:
        dict: 
    """

    sr_agr_score = df_top5.loc[user_name].groupby('category')['score'].sum()
    dict_score = sr_agr_score.to_dict()

    return dict_score


def create_trace(list_category, dict_score: dict, user_name: str):
    # TOP5に存在しない資質カテゴリはスコアを0にする
    for _categry in list_category:
        if not _categry in dict_score:
            dict_score[_categry] = 0

    dict_score = dict(sorted(dict_score.items()))
    trace = go.Scatterpolar(
        r=list(dict_score.values()),
        theta=list(dict_score.keys()),
        fill='toself',
        name=user_name,
        opacity=0.9,
        marker=dict(
            symbol="square",
            size=8
        ),
    )

    return trace


@app.callback(Output('team_feature', 'figure'), [Input('team_users', 'value')])
def update_graph(list_user):
    dict_rank_to_score = {1: 5, 2: 4, 3: 3, 4: 2, 5: 1}

    df_top5['category'] = df_top5[['strengths']
                                  ].applymap(dict_strengths_category.get)
    df_top5['score'] = df_top5[['rank']].applymap(dict_rank_to_score.get)

    data = []

    # 初期化
    dict_scores = {}
    for _categry in list_category:
        dict_scores[_categry] = 0

    for _user in list_user:
        dict_score = calc_score(df_top5, _user)
        dict_score = dict(sorted(dict_score.items()))
        for _categry, _score in dict_score.items():
            dict_scores[_categry] += _score

        trace = create_trace(list_category, dict_score, _user)
        data.append(trace)

    dict_scores = dict(sorted(dict_scores.items()))

    trace0 = go.Scatterpolar(
        r=list(dict_scores.values()),
        theta=list(dict_scores.keys()),
        fill='toself',
        fillcolor='gray',
        name='合計',
        opacity=0.7,
        marker=dict(symbol="square",
                    size=8
                    ),
        line=dict(color='black'),
        subplot='polar2'
    )

    data.append(trace0)

    ann1 = dict(font=dict(size=14),
                showarrow=False,
                text='合計スコア',
                # Specify text position (place text in a hole of pie)
                x=0.16,
                y=1.18
                )
    ann2 = dict(font=dict(size=14),
                showarrow=False,
                text='各人のスコア',
                x=0.85,
                y=1.18
                )

    layout = go.Layout(
        annotations=[ann1, ann2],
        showlegend=True,
        polar2=dict(domain=dict(x=[0, 0.4],
                                y=[0, 1]
                                ),
                    radialaxis=dict(tickfont=dict(size=8)),
                    ),
        polar=dict(domain=dict(x=[0.6, 1],
                               y=[0, 1]
                               ),
                   radialaxis=dict(tickfont=dict(size=8)),
                   )
    )

    return {'data': data, 'layout': layout}


# ------------------------------------------------------------------------------
# 機能1 グループの傾向把握: layout に追加するコンポーネント作成
# ------------------------------------------------------------------------------

header_contents = html.Div(
    [
        html.H5('グループの傾向把握',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P('※参照したい方の氏名を入力してください（複数入力）')
    ]
)


# ------------------------------------------------------------------------------
# 機能2 グループ内で不足している資質: callback の設定
# ------------------------------------------------------------------------------

# settings
topN = 10  # topN位以上の資質が含まれていれば足りない資質ではないとする
output_num = 2  # 最大でいくつの資質を出力するか


def list2markdown(list_message):
    """
    資質の説明message(リスト形式)をマークダウンに変換
    """
    list_message = ['・' + x for x in list_message]
    str_message = '  \n '.join(list_message)
    return str_message


def create_markdown_text_with_lack(dict_strengths_message, dict_lack_result, index_num):
    strengths_name = dict_lack_result['strengths'][index_num]
    list_message = dict_strengths_message[strengths_name]['長所']
    strengths_message = list2markdown(list_message)
    strengths_mean = dict_lack_result['mean'][index_num]
    strengths_min = dict_lack_result['min'][index_num]

    text = """
    #### {0}
    
    {1}  
    ***
    このグループ内の {0} の平均順位は**{2}位**、  
    最高順位は**{3}位**です。
    """.format(strengths_name, strengths_message, strengths_mean, strengths_min)
    return text


def aggregate(df):
    # 各資質の平均と最小値集計
    df_mean = df.groupby('strengths').mean()
    sr_mean = df_mean['rank'].map(lambda x: int(
        Decimal(str(x)).quantize(Decimal('0'), rounding=ROUND_HALF_UP)))

    df_min = df.groupby('strengths').min()

    df_aggregate = pd.concat([sr_mean, df_min], axis=1)
    df_aggregate.columns = ['mean', 'min']

    return df_aggregate


def lack_strengths_in_team(df_org, target_users, topN, output_num):
    # データ抽出
    df = df_org.loc[target_users]

    # 各資質の平均と最小値集計
    df_aggregate = aggregate(df)

    # 最小値がN位以内の資質を削除
    df_under = df_aggregate[df_aggregate['min'] > topN].sort_values('mean')[
        ::-1]

    # 平均が高い上位2つの資質を抽出
    df_weakly = df_under.head(output_num)
    dict_weakly_info = df_weakly.reset_index().to_dict(orient='list')

    return dict_weakly_info


@app.callback(Output('lack_strengths_1', 'children'),
              [Input('team_users', 'value')])
def update_lack_strength_1(list_user):
    dict_lack_result = lack_strengths_in_team(
        df_all, list_user, topN, output_num)
    text = create_markdown_text_with_lack(
        dict_strengths_message, dict_lack_result, 0)
    return text


@app.callback(Output('lack_strengths_2', 'children'),
              [Input('team_users', 'value')])
def update_lack_strength_2(list_user):
    dict_lack_result = lack_strengths_in_team(
        df_all, list_user, topN, output_num)
    text = create_markdown_text_with_lack(
        dict_strengths_message, dict_lack_result, 1)
    return text


# ------------------------------------------------------------------------------
# 機能2 グループ内で不足している資質: layout に追加するコンポーネントの作成
# ------------------------------------------------------------------------------
lack_strengths_content = html.Div(
    [
        html.H5('グループ内に不足している強み',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P('')
    ]
)

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

lack_strengths_cards_row = dbc.Row(
    [
        dbc.Col(dbc.Card(card_content_lack_strengths1, color="danger",
                         outline=True), width=4),
        dbc.Col(dbc.Card(card_content_lack_strengths2, color="danger",
                         outline=True), width=4),
    ],
    className="mb-4"
)


# ------------------------------------------------------------------------------
# 機能3 グループ内における個人のユニークな強み: callback の設定
# ------------------------------------------------------------------------------

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


def extract_unique_strength(df, target_user, member_name_list, top_n=2):
    """

    Args:
        df (pd.DataFrame): 全ユーザの資質ランキング（前処理前）
        target_user (str): ユーザー名
        member_name_list (list): 
        top_n (int): 上位何位までの資質を計算するか

    Returns:
        list: 
    """

    extracted_member_df = merge_series(df, member_name_list) + 1
    extracted_target_series = extract_series(df, target_user) + 1
    computed_prominent = pd.concat([compute_prominent_attribute(
        extracted_target_series, extracted_member_df), extracted_target_series, extracted_member_df.mean(axis=1)], axis=1, sort=False)

    top_n_prominent = computed_prominent.tail(top_n)

    return top_n_prominent.index.values[::-1], top_n_prominent[1].values[::-1], top_n_prominent[2].values[::-1]


def create_markdown_text(dict_strengths_message, dict_result, index_num, target_user):
    strengths_name = dict_result['strengths'][index_num]
    list_message = dict_strengths_message[strengths_name]['長所']
    strengths_message = list2markdown(list_message)
    strengths_mean = dict_result['member_avg_rank'][index_num]
    target_rank = dict_result['target_rank'][index_num]

    text = """
    #### {0}
    
    {1}  
    ***
    このグループ内の {0} の平均順位は**{2}位**、  
    {3} さんの順位は**{4}位**です。
    """.format(strengths_name, strengths_message, strengths_mean, target_user, target_rank)
    return text


def main_extract_unique_strength(df, target_user, member_name_list, top_n=2):
    """

    Args:

    Returns:

    """

    # target_user = "氏名1"
    # member_name_list = ['氏名1', '氏名2', ...]

    member_name_list.remove(target_user)
    strength, target_rank, member_average_rank = extract_unique_strength(
        df, target_user, member_name_list, top_n)

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


@app.callback(
    Output('user_drop_down', 'options'),
    [Input('team_users', 'value')])
def set_cities_options(selected_user):
    return [{'label': i, 'value': i} for i in selected_user]


@app.callback(Output('user_drop_down', 'value'),
              [Input('user_drop_down', 'options')])
def set_cities_value(available_options):
    return available_options[0]['value']


@app.callback(Output('target_user', 'children'),
              [Input('team_users', 'value'),
               Input('user_drop_down', 'value')])
def update_unique_strestrength(list_user, target_user):
    text = 'このグループ内における {} さんのユニークな強みは下記の通りです。'.format(target_user)
    return text


@app.callback(Output('unique_strengths_1', 'children'),
              [Input('team_users', 'value'),
               Input('user_drop_down', 'value')])
def update_unique_strestrength_1(list_user, target_user):
    dict_result = main_extract_unique_strength(
        df_strength_org, target_user, list_user)
    text = create_markdown_text(
        dict_strengths_message, dict_result, 0, target_user)
    return text


@app.callback(Output('unique_strengths_2', 'children'),
              [Input('team_users', 'value'),
               Input('user_drop_down', 'value')])
def update_unique_strestrength_2(list_user, target_user):
    dict_result = main_extract_unique_strength(
        df_strength_org, target_user, list_user)
    text = create_markdown_text(
        dict_strengths_message, dict_result, 1, target_user)
    return text


# ------------------------------------------------------------------------------
# 機能3 グループ内における個人のユニークな強み: layout に追加するコンポーネントの作成
# ------------------------------------------------------------------------------

unique_strengths_content = html.Div(
    [
        html.H5('グループ内における個人のユニークな強み',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P('強みを知りたい人を選択してください')
    ]
)

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


unique_strengths_cards_row = dbc.Row(
    [
        dbc.Col(dbc.Card(card_content_unique_strengths1, color="primary",
                         outline=True), width=4),
        dbc.Col(dbc.Card(card_content_unique_strengths2, color="primary",
                         outline=True), width=4)
    ],
    className="mb-4",
)


# ------------------------------------------------------------------------------
# 各機能のコンポーネントで layout を構築
# ------------------------------------------------------------------------------

unique_users = np.unique(df_top5.index)

users_drop_down_list = dcc.Dropdown(
    id='team_users',
    options=[{'label': i, 'value': i}
             for i in unique_users],
    multi=True
)

layout = html.Div(
    [
        header_contents,
        users_drop_down_list,

        # 機能1 グループの傾向表示
        dcc.Graph(id='team_feature'),

        # 機能2 グループ内で不足している資質表示
        lack_strengths_content,
        lack_strengths_cards_row,

        # 機能3 グループ内における個人のユニークな強み
        unique_strengths_content,
        dcc.RadioItems(id='user_drop_down'),
        dcc.Markdown(id='target_user'),
        unique_strengths_cards_row,
    ],
)
