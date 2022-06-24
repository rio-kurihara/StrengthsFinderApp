import os
from decimal import ROUND_HALF_UP, Decimal

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly
import plotly.graph_objs as go
import yaml
from app import app
from dash import dcc, html
from dash.dependencies import Input, Output
from dotenv import load_dotenv

# from src.app import app  # pytest のときのみこっち


# .envから環境変数を読み込む
load_dotenv()

# settings.yaml の読み込み
with open('settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

# パスを設定
bucket_name = os.getenv('BUCKET_NAME')
bucket_path = 'gs://{}/'.format(bucket_name)
mst_category_path = bucket_path + config['mst_category_path']
mst_message_json_path = bucket_path + config['mst_message_json_path']
strengths_path = bucket_path + config['strengths_path']
top5_path = bucket_path + config['top5_path']
all34_path = bucket_path + config['all34_path']
all34_exsits_null_path = bucket_path + config['all34_exsits_null_path']

# GCS のバケットからファイルを読み込む
df_mst = pd.read_csv(mst_category_path)
df_strength_org = pd.read_csv(strengths_path)
df_top5 = pd.read_csv(top5_path, index_col='user_name')
df_all = pd.read_csv(all34_path)
df_all_exsits_null = pd.read_csv(all34_exsits_null_path, index_col='user_name')
df_all_exsits_null = df_all_exsits_null.fillna('nan')
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
    if len(list_users) <= 1:
        return None
    else:
        dict_lack_result = lack_strengths_in_team(df_all_exsits_null, list_users)
        text = create_display_text_for_lack(
            dict_strengths_message, dict_lack_result, 0)
        return text


@app.callback(Output('lack_strengths_2', 'children'),
              [Input('team_users', 'value')])
def update_lack_strength_2(list_users):
    if len(list_users) <= 1:
        return None
    else:
        dict_lack_result = lack_strengths_in_team(df_all_exsits_null, list_users)
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
    # 表示の見やすさのため、平均順位を四捨五入する
    member_average_rank = [int(Decimal(str(x)).quantize(
        Decimal('0'), rounding=ROUND_HALF_UP)) for x in dict_result['member_avg_rank']]
    strengths_mean = member_average_rank[index_num]
    target_rank = dict_result['target_rank'][index_num]

    text = """
    #### {0}
    
    {1}  
    ***
    このグループ内の {0} の平均順位は**{2}位**、  
    {3} さんの順位は**{4}位**です。
    """.format(strengths_name, strengths_message, strengths_mean, target_user, target_rank)

    return text


def calc_rank_diff(df: pd.DataFrame, group_users: list, target_user: str) -> pd.DataFrame:
    """
    資質別に、対象ユーザーとグループメンバーの順位の差分を計算

    Args:
        df (pd.DataFrame): 資質名とその順位を含むデータフレーム。indexが資質、列がユーザー。
        group_users (list): 集計対象グループのユーザー（複数）※上記 target_user を含むリスト
        target_user (str): 着目したいユーザー名
    Returns:
        df (pd.DataFrame): 対象ユーザーとグループメンバーの順位の差分
    """
    group_users_cp = group_users.copy()
    group_users_cp.remove(target_user)
    df_diff = pd.DataFrame()

    for _user_name in group_users_cp:
        # グループメンバーの順位から対象ユーザーの順位を引く
        sr_diff_tmp = df[_user_name] - df[target_user]
        sr_diff_tmp.name = _user_name
        df_diff = pd.concat([df_diff, sr_diff_tmp], axis=1)

    return df_diff


def extract_unique_strength(
    df: pd.DataFrame, group_users: list, target_user: str, top_n=2
) -> dict:
    """
    資質別に、対象ユーザーとグループメンバーの順位の差分を計算

    Args:
        df (pd.DataFrame): 34の資質が全てオープンになっているユーザーのみのデータ
                           列名: user_name, strengths, rank, deparment
        group_users (list): 集計対象グループのユーザー（複数）※上記 target_user 含むリスト
        target_user (str): 着目したいユーザー名
        top_n (int, optional): 上位何位までの結果を出力するか. デフォルトは 2

    Returns:
        dict: 例
            dict_result = {'strengths': ['公平性' '調和性'], # ユニークな資質名
                        'target_rank': [9, 3], # 着目したユーザーの資質順位
                        'member_avg_rank': [31., 24.] # グループ内の平均順位
                        }
    """
    # 集計対象のグループメンバーのデータを抽出
    df_extracted_group = df[df['user_name'].isin(group_users)]
    # 行に資質、列にユーザーとなるようにピボットする
    df_extracted_group_pivot = df_extracted_group.pivot_table(
        index="strengths", columns="user_name", values="rank")

    # 資質別に、対象ユーザーとグループメンバーの順位の差分を計算
    df_diff = calc_rank_diff(df_extracted_group_pivot, group_users, target_user)

    # 順位差分の合計を計算
    sr_diff_total = df_diff.sum(axis=1)
    # 順位差分にランクをつける
    df_diff_rank = df_diff.rank(method='first', axis=1, ascending=False)

    # 順位差分を降順で上から2番目の差分の値を取得
    # 対象グループのユーザーが二名の場合のみ、順位差分の上から二番目が取れないため以下の処理とする
    if len(group_users) == 2:
        # フラグ用のデータフレームの全ての値を True にする
        col_name = df_diff.columns
        df_flag = df_diff.copy()
        df_flag.loc[:, col_name] = True
    else:
        # 順位差分を降順で上から2番目の差分の値を取得
        df_flag = df_diff_rank.applymap(lambda x: True if x == 2 else False)
    # True の数が34になるか確認
    assert df_flag.sum().sum() == 34
    diff_total_second = df_diff[df_flag].sum(axis=1)
    # ユニークスコアの計算：順位差分の合計と、順位差分の上から二番目の値を合計する
    df_result = pd.concat([sr_diff_total, diff_total_second], axis=1)
    df_result.columns = ['diff_total', 'diff_second']
    df_result['unique_score'] = df_result['diff_total'] + df_result['diff_second']
    # ユニークスコアを降順にソート
    df_result = df_result.sort_values('unique_score', ascending=False)
    # ユニークな資質を取得：ユニークスコア上位 N 位の資質
    unique_strength_names = list(df_result.head(top_n).index)
    # ユニークな資質の順位を取得
    unique_strengths_rank = df_extracted_group_pivot[target_user].loc[unique_strength_names].values
    # 対象ユーザー以外のグループユーザーの平均順位を計算
    group_users.remove(target_user)
    sr_mean = df_extracted_group_pivot[group_users].mean(axis=1)
    # 対象ユーザーのユニークな強みについて、他ユーザーの平均順位を取得
    unique_strengths_mean = sr_mean.loc[unique_strength_names].values

    dict_result = {'strengths': unique_strength_names,
                   'target_rank': list(unique_strengths_rank),
                   'member_avg_rank': list(unique_strengths_mean)
                   }

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
    if len(list_users) <= 1:
        return None
    else:
        text = 'このグループ内における {} さんのユニークな強みは下記の通りです。'.format(target_user)
        return text


@app.callback(Output('unique_strengths_1', 'children'),
              [Input('team_users', 'value'),
               Input('user_drop_down', 'value')])
def update_unique_strestrength_1(list_users, target_user):
    if len(list_users) <= 1:
        return None
    else:
        dict_result = extract_unique_strength(
            df_all, list_users, target_user)
        text = create_display_text_for_unique(
            dict_strengths_message, dict_result, 0, target_user)
        return text


@app.callback(Output('unique_strengths_2', 'children'),
              [Input('team_users', 'value'),
               Input('user_drop_down', 'value')])
def update_unique_strestrength_2(list_users, target_user):
    if len(list_users) <= 1:
        return None
    else:
        dict_result = extract_unique_strength(
            df_all, list_users, target_user)
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
