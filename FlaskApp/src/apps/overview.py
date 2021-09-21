from google.cloud import storage
import copy
import pickle

import pandas as pd
import plotly.graph_objs as go
import yaml
from dash import dcc, html

# settings
with open('settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)
top5_path = config['base_dir'] + config['top5_path']
all34_path = config['base_dir'] + config['all34_path']
colors_strengths_path = config['base_dir'] + config['colors_strengths_path']
bucket_name = config['bucket_name']


# load data
df_top5 = pd.read_csv(top5_path, index_col='index')
df_all34 = pd.read_csv(all34_path, index_col='index')
dict_colors_strengths = pd.read_pickle(colors_strengths_path)


def create_graph_strengths_rank_sum(rank_sum_each_departments, dict_colors_strengths, department):
    """各資質の順位合計のグラフオブジェクトを作成

    横軸は資質名、縦軸は合計順位

    Args:
        rank_sum_each_departments (pd.Series): 各部署の資質ごとの順位合計
        dict_colors_strengths (dict): 各資質のカラーコード
                                    ex: {'責任感': '#ffbcdd', '達成欲': '#ffbcdd', ...}
        department (list): 所属名のリスト

    Returns:
        list: グラフオブジェクトのリスト
    """

    unique_strengths = dict_colors_strengths.keys()

    if department in departments:
        sr_score = rank_sum_each_departments.loc[department].sort_values()[::-1]
        list_unknown = list(set(unique_strengths) - set(sr_score.index))

        x = list(sr_score.index)
        x += list_unknown
        y = list(sr_score.values)
        y += [-1 for x in list_unknown]

        marker = dict(
            color=[dict_colors_strengths[_strengths] for _strengths in x]
        )

        trace0 = go.Bar(
            x=x,
            y=y,
            marker=marker,
        )

        data = [trace0]

    else:
        data = []

    return data


def create_graph_registered_user_cnt(df_top5, df_all34):
    """部署別の登録ユーザー数のグラフオブジェクトを作成

    TOP5のみ登録しているユーザー数と、全資質を登録しているユーザー数をグラフ化する
    横軸は所属、縦軸は登録ユーザー数

    Args:
        df_top5 (pd.DataFrame): 全ユーザーの資質ランキング(TOP5のみ)
        df_all34 (pd.DataFrame): 全ユーザーの資質ランキング

    Returns:
        list: グラフオブジェクトのリスト
    """

    y0, y1 = [], []

    for department in departments:
        df_tmp_top5 = df_top5[df_top5['department'] == department]
        df_tmp_all34 = df_all34[df_all34['department'] == department]

        if not (len(df_tmp_all34) == 0 and len(df_tmp_top5) == 0):
            set_top5_person = set(list(df_tmp_top5.index))
            set_all34_person = set(list(df_tmp_all34.index))

            y0.append(len(set_all34_person))
            y1.append(len(set_top5_person) - len(set_all34_person))
        else:
            y0.append(0)
            y1.append(0)

    trace0 = go.Bar(
        x=departments,
        y=y0,
        name='全資質オープン済'
    )
    trace1 = go.Bar(
        x=departments,
        y=y1,
        name='TOP5のみ'
    )

    data = [trace0, trace1]

    return data


# 集計対象の部署名を設定
departments = config['departments']
departments.remove("retiree")

header_contents = html.Div(
    [
        html.H5('診断済み社員数：{}名'.format(len(set(df_top5.index))),
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P('')
    ]
)

title_contents = html.Div(
    [
        html.H5('資質ランキング',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")
                ),
        html.P('')
    ]
)

graph_registered_user_cnt_each_division = html.Div(
    dcc.Graph(
        id='cnt',
        figure={
            'data': create_graph_registered_user_cnt(df_top5, df_all34),
            'layout': {
                'barmode': 'stack',
                'title': '部署別診断済みの社員数',
                'yaxis': dict(title='人数'),
                'xaxis': dict(title='本部')
            }
        }
    ),
    style={'display': 'inline-block'}
)


layout = [
    header_contents,
    graph_registered_user_cnt_each_division,
    title_contents
]

# 各部署の資質ごとの順位合計を計算
rank_sum_each_departments = df_top5.groupby(['department', 'strengths'])['score'].sum()

# 部署別の資質ランキングのグラフを作成
for i, department in enumerate(departments):
    graph_rank_sum_each_department = html.Div(
        dcc.Graph(
            id='score_summary{}'.format(i+1),
            figure={
                'data': create_graph_strengths_rank_sum(rank_sum_each_departments, dict_colors_strengths, department),
                'layout': {
                    'title': '資質の合計スコア({})'.format(department)
                }
            }
        ),
        style={'display': 'inline-block'})

    layout.append(graph_rank_sum_each_department)
