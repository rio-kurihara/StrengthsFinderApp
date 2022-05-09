import json
import os
import sys
from decimal import ROUND_HALF_UP, Decimal

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly
import plotly.graph_objs as go
import yaml
from dash import dcc, html
from dash.dependencies import Input, Output

from app import app
# from src.app import app  # pytest のときのみこっち


# settings.yaml の読み込み
with open('src/settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

# パスを設定
base_dir = config['base_dir']
mst_category_path = base_dir + config['mst_category_path']
mst_message_json_path = base_dir + config['mst_message_json_path']
strengths_path = base_dir + config['strengths_path']
top5_path = base_dir + config['top5_path']
all34_path = base_dir + config['all34_path']
all34_exsits_null_path = base_dir + config['all34_exsits_null_path']

# GCS のバケットからファイルを読み込む
df_mst = pd.read_csv(mst_category_path)
df_strength_org = pd.read_csv(strengths_path)
df_top5 = pd.read_csv(top5_path, index_col='user_name')
df_all = pd.read_csv(all34_exsits_null_path, index_col='user_name')
df_all = df_all.fillna('nan')
dict_strengths_message = pd.read_json(mst_message_json_path)

# 資質カテゴリーの設定
list_category = df_mst['category'].unique()
dict_strengths_category = df_mst.set_index('strengths')['category'].to_dict()


# ------------------------------------------------------------------------------
# 機能1 グループの傾向把握: callbackの設定
# ------------------------------------------------------------------------------

def sum_rank_each_strengths_category(
    df_top5: pd.DataFrame, user_name: str
) -> dict:
    """ 4つの資質カテゴリーごとに順位を合計する

    Args:
        df_top5 (pd.DataFrame): 全ユーザーの資質ランキング
        user_name (str): 集計対象のユーザー名

    Returns:
        dict: 例 {'人間関係構築力': 6, '実行力': 4, '影響力': 3, '戦略的思考力': 2}
    """

    df_target_user = df_top5.loc[user_name]

    # 4つの資質カテゴリーごとに順位を合計する
    sr_agr_score = df_target_user.groupby('category')['score'].sum()
    dict_scores = sr_agr_score.to_dict()

    return dict_scores


def create_graph_objs(
    list_category: list, dict_scores: dict, user_name: str
) -> plotly.graph_objs:
    """ 

    Args:
        list_category (list): 
        dict_scores (dict): カテゴリごとの資質順位合計
            例: {'人間関係構築力': 6, '実行力': 4, '影響力': 3, '戦略的思考力': 2}
        user_name (str): 集計対象のユーザー名

    Returns:
        plotly.graph_objs
    """

    # TOP5 に存在しない資質カテゴリはスコアを 0 にする
    for _categry in list_category:
        if not _categry in dict_scores:
            dict_scores[_categry] = 0

    # dict_scores = dict(sorted(dict_scores.items()))

    trace = go.Scatterpolar(
        r=list(dict_scores.values()),
        theta=list(dict_scores.keys()),
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
def update_graph(list_users):
    dict_rank_to_score = {1: 5, 2: 4, 3: 3, 4: 2, 5: 1}

    df_top5['category'] = df_top5[['strengths']
                                  ].applymap(dict_strengths_category.get)
    df_top5['score'] = df_top5[['rank']].applymap(dict_rank_to_score.get)

    data = []

    team_scores_by_category = {}

    for _categry in list_category:
        team_scores_by_category[_categry] = 0

    for _user in list_users:
        # 1ユーザーのカテゴリごとの資質順位合計を計算
        user_scores_by_category = sum_rank_each_strengths_category(df_top5, _user)
        # user_scores_by_category = dict(sorted(user_scores_by_category.items()))

        for _categry, _score in user_scores_by_category.items():
            team_scores_by_category[_categry] += _score

        # グラフオブジェクトの作成
        trace = create_graph_objs(list_category, user_scores_by_category, _user)
        data.append(trace)

    # チーム全体のカテゴリごとの資質順位合計を取得
    team_scores_by_category = dict(sorted(team_scores_by_category.items()))
    team_scores = list(team_scores_by_category.values())
    categorys = list(team_scores_by_category.keys())

    trace0 = go.Scatterpolar(
        r=team_scores,
        theta=categorys,
        fill='toself',
        fillcolor='gray',
        name='合計',
        opacity=0.7,
        marker=dict(symbol="square", size=8),
        line=dict(color='black'),
        subplot='polar2'
    )

    data.append(trace0)

    ann1 = dict(
        font=dict(size=14),
        showarrow=False,
        text='合計スコア',
        # Specify text position (place text in a hole of pie)
        x=0.16,
        y=1.18
    )
    ann2 = dict(
        font=dict(size=14),
        showarrow=False,
        text='各人のスコア',
        x=0.85,
        y=1.18
    )

    layout = go.Layout(
        annotations=[ann1, ann2],
        showlegend=True,
        polar2=dict(
            domain=dict(x=[0, 0.4],
                        y=[0, 1]
                        ),
            radialaxis=dict(tickfont=dict(size=8)),
        ),
        polar=dict(
            domain=dict(x=[0.6, 1],
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

def list_to_bullets_str(list_messages: list) -> str:
    """描画のために、資質の説明（リスト形式）を箇条書きテキストに変換

    Args:
        list_message (list): 各資質の意味を説明するテキストのリスト
            例: ['勤勉にコツコツ努力することができる',
                 'チームの生産性を上げる',
                 '時間を無駄にせず、効率的にたくさんの仕事を終わらせる']

    Returns:
        str: 全ての説明を結合した文字列
    """
    # 描画のために、箇条書き '・' を文字列の頭に追加
    list_messages = ['・' + x for x in list_messages]
    # 全ての文字列を改行コードを入れて結合する
    str_message = '  \n '.join(list_messages)

    return str_message


def create_display_text_for_lack(
        dict_strengths_message: dict, dict_lack_result: dict, target_index: int
) -> str:
    """「チーム内に不足している資質提示」機能における、表示用のテキストを作成

    Args:
        dict_strengths_message (dict): 全資質の意味を説明するテキストを含む辞書 (key=資質名, value=説明テキスト)
        dict_lack_result (dict): チームに不足していると判定された資質の情報を含む辞書
            例: {'strengths': ['公平性', '慎重さ'], 'mean': [34, 35], 'min': [34, 33]}
                (strengths: 不足している資質, mean: チーム内の平均順位, min: チーム内の最低順位)
        index_num (int): 不足している資質のうち、何番目の資質の情報を生成するか

    Returns:
        str: 表示用のテキスト
    """
    # 対象の資質名を取得
    strengths_name = dict_lack_result['strengths'][target_index]
    # 対象の資質の説明テキストを取得
    list_message = dict_strengths_message[strengths_name]['長所']
    strengths_message = list_to_bullets_str(list_message)
    # チーム内における、対象の資質の平均順位と最低順位を取得
    strengths_mean = dict_lack_result['mean'][target_index]
    strengths_min = dict_lack_result['min'][target_index]

    # 表示用のテキストを生成
    text = """
    #### {0}
    
    {1}  
    ***
    このグループ内の {0} の平均順位は**{2}位**、  
    最高順位は**{3}位**です。
    """.format(strengths_name, strengths_message, strengths_mean, strengths_min)

    return text


def calc_mean_and_min(df: pd.DataFrame) -> pd.DataFrame:
    """資質ごとに、チーム内の平均と最小値を集計

    Args:
        df (pd.DataFrame): 資質名とその順位を含むデータフレーム。氏名がindex。

    Returns:
        pd.DataFrame: 資質ごとの平均値と最小値を含むデータフレーム。資質名がindex。
    """
    # 各資質の平均と最小値集計
    df_mean = df.groupby('strengths').mean()
    sr_mean = df_mean['rank'].map(
        lambda x: int(
            Decimal(str(x)).quantize(Decimal('0'), rounding=ROUND_HALF_UP)
        )
    )
    df_min = df.groupby('strengths').min()

    df_aggregate = pd.concat([sr_mean, df_min], axis=1)
    df_aggregate.columns = ['mean', 'min']

    return df_aggregate


def lack_strengths_in_team(
    df_org: pd.DataFrame, target_users: list, topN: int = 10, output_num: int = 2
) -> dict:
    """チーム内で不足している資質を集計する

    Args:
        df_org (pd.DataFrame): 資質名とその順位を含むデータフレーム。氏名がindex。
        target_users (list): 集計対象のユーザー
        topN (int): チーム内の誰かしらが、topN 以上を持っていれば、足りている資質とする
        output_num (int): 最大でいくつの資質を出力するか

    Returns:
        dict: チームに不足していると判定された資質の情報を含む辞書
            例: {'strengths': ['公平性', '慎重さ'], 'mean': [34, 35]:, 'min: [34, 33]}
    """
    # 対象ユーザーのデータ抽出
    df = df_org.loc[target_users]

    # 各資質の平均と最小値集計
    df_aggregate = calc_mean_and_min(df)

    # 最小値が N 位以内の資質を削除
    df_under = df_aggregate[df_aggregate['min'] > topN]
    df_under = df_under.sort_values('mean')[::-1]

    # 平均値が高い(=順位が低い))上位2つの資質を抽出
    df_weakly = df_under.head(output_num)
    dict_lack_strengths_info = df_weakly.reset_index().to_dict(orient='list')

    return dict_lack_strengths_info


@app.callback(Output('lack_strengths_1', 'children'),
              [Input('team_users', 'value')])
def update_lack_strength_1(list_users):
    dict_lack_result = lack_strengths_in_team(df_all, list_users)
    text = create_display_text_for_lack(
        dict_strengths_message, dict_lack_result, 0)
    return text


@app.callback(Output('lack_strengths_2', 'children'),
              [Input('team_users', 'value')])
def update_lack_strength_2(list_users):
    dict_lack_result = lack_strengths_in_team(df_all, list_users)
    text = create_display_text_for_lack(
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


def extract_unique_strength(
    df: pd.DataFrame, target_user: str, list_users: list, top_n: int = 2
) -> list:
    """
    チーム内における、個人の突出した強みを集計

    Args:
        df (pd.DataFrame): 資質名とその順位を含むデータフレーム。氏名がindex。
        target_user (str): ユーザー名
        list_users (list): ユーザー名（複数）
        top_n (int): 上位何位までの資質を計算するか

    Returns:
        ※TODO: 複数の戻り値やめる
    """
    # 対象ユーザーのデータを抽出
    # 順位を 1 始まりにするため +1 する
    extracted_member_df = merge_series(df, list_users) + 1
    extracted_target_series = extract_series(df, target_user) + 1

    prominent_scores = compute_prominent_attribute(extracted_target_series, extracted_member_df)
    sr_mean = extracted_member_df.mean(axis=1)

    # TODO:全体的に処理がわかりづらい。綺麗にする
    # 下位 top_n 位の資質名を抽出
    # lack_strength_names = prominent_scores.tail(top_n).index[::-1]
    # strength_means = sr_mean.loc[lack_strength_names].values
    # strength_ranks = extracted_target_series.loc[lack_strength_names].values

    computed_prominent = pd.concat([prominent_scores, extracted_target_series, sr_mean],
                                   axis=1, sort=False)
    unique_strengths_info = computed_prominent.tail(top_n)
    strength_names = unique_strengths_info.index.values[::-1]
    strength_ranks = unique_strengths_info[1].values[::-1]
    strength_means = unique_strengths_info[2].values[::-1]

    return strength_names, strength_ranks, strength_means


def create_display_text_for_unique(
    dict_strengths_message: dict, dict_result: dict, index_num: int, target_user: str
) -> str:
    """「チームにおける個人のユニークな強み提示」機能における、表示用のテキストを作成

    Args:
        dict_strengths_message (dict): 全資質の意味を説明するテキストを含む辞書 (key=資質名, value=説明テキスト)
        dict_result (dict): ユニークな資質と判定された資質の情報を含む辞書
        index_num (int): ユニークな資質のうち、何番目の資質の情報を生成するか
        target_user (str): 対象のユーザー名

    Returns:
        str: 表示用のテキスト
    """
    strengths_name = dict_result['strengths'][index_num]
    list_message = dict_strengths_message[strengths_name]['長所']
    strengths_message = list_to_bullets_str(list_message)
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


def main_extract_unique_strength(
    df: pd.DataFrame, target_user: str, member_name_list: list, top_n=2
) -> dict:
    """
    main_extract_unique_strength [summary]

    [extended_summary]

    Args:
        df (pd.DataFrame): [description]
        target_user (str): [description]
        member_name_list (list): [description]
        top_n (int, optional): [description]. Defaults to 2.

    Returns:
        dict: [description]
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
def update_unique_strestrength(list_users, target_user):
    text = 'このグループ内における {} さんのユニークな強みは下記の通りです。'.format(target_user)
    return text


@app.callback(Output('unique_strengths_1', 'children'),
              [Input('team_users', 'value'),
               Input('user_drop_down', 'value')])
def update_unique_strestrength_1(list_users, target_user):
    dict_result = main_extract_unique_strength(
        df_strength_org, target_user, list_users)
    text = create_display_text_for_unique(
        dict_strengths_message, dict_result, 0, target_user)
    return text


@app.callback(Output('unique_strengths_2', 'children'),
              [Input('team_users', 'value'),
               Input('user_drop_down', 'value')])
def update_unique_strestrength_2(list_users, target_user):
    dict_result = main_extract_unique_strength(
        df_strength_org, target_user, list_users)
    text = create_display_text_for_unique(
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
