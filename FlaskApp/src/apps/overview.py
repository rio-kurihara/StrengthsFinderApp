import copy
import os

import pandas as pd
import plotly.graph_objs as go
import yaml
from dash import dcc, html
from dotenv import load_dotenv
from google.cloud import storage

# .envから環境変数を読み込む
load_dotenv()

# settings.yaml の読み込み
with open('src/settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

# パスを設定
bucket_name = os.getenv('BUCKET_NAME')
bucket_path = 'gs://{}/'.format(bucket_name)
top5_path = bucket_path + config['top5_path']
all34_path = bucket_path + config['all34_path']
colors_strengths_path = bucket_path + config['colors_strengths_path']

# 集計対象の部署名を設定
departments = config['departments']
departments.remove("retiree")

# GCS のバケットからファイルを読み込む
df_top5 = pd.read_csv(top5_path, index_col='user_name')
df_all34 = pd.read_csv(all34_path, index_col='user_name')
dict_colors_strengths = pd.read_pickle(colors_strengths_path)


def create_graph_strengths_rank_sum(
        rank_sum_each_departments: pd.Series,
        dict_colors_strengths: dict,
        department: str
) -> list:
    """各資質の順位合計のグラフオブジェクトを作成

    横軸は資質名、縦軸は合計順位

    Args:
        rank_sum_each_departments (pd.Series): 各部署の資質ごとの順位合計
        dict_colors_strengths (dict): 各資質のカラーコード
                                    ex: {'責任感': '#ffbcdd', '達成欲': '#ffbcdd', ...}
        department (str): 所属名のリスト

    Returns:
        list: グラフオブジェクトのリスト
    """

    # 全種類の資質名をリストで準備
    unique_strengths = dict_colors_strengths.keys()

    # 指定された所属が所属リストに含まれていなければ何も表示しない
    if not department in departments:
        data = []
        return data

    # 指定された所属が所属リストにあれば
    else:
        rank_sum_target_department = rank_sum_each_departments.loc[department].sort_values()[::-1]

        # 全資質から部署が持っていない資質を抽出
        missing_strengths = list(set(unique_strengths) - set(rank_sum_target_department.index))

        # 描画のために x, y それぞれで持っていない資質をリストの後ろへ配置
        x = list(rank_sum_target_department.index)
        x += missing_strengths
        y = list(rank_sum_target_department.values)
        y += [-1 for x in missing_strengths]

        marker = dict(
            color=[dict_colors_strengths[_strengths] for _strengths in x]
        )

        trace0 = go.Bar(
            x=x,
            y=y,
            marker=marker,
        )

        data = [trace0]

    return data


def create_graph_registered_user_cnt(df_top5: pd.DataFrame, df_all34: pd.DataFrame) -> list:
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
        # 部署の top5 と all34 を抽出
        df_top5_department = df_top5[df_top5['department'] == department]
        df_all34_department = df_all34[df_all34['department'] == department]

        # top5 と all34 の両方とも資質データが存在しない場合
        if (len(df_all34_department) == 0 and len(df_top5_department) == 0):
            # 描画のために 0 を追加
            y0.append(0)
            y1.append(0)

        else:
            # ユニークなユーザーを抽出
            top5_unique_users = set(list(df_top5_department.index))
            all34_unique_users = set(list(df_all34_department.index))

            # 描画のためユニークユーザー数を Y 軸に追加
            y0.append(len(top5_unique_users))
            y1.append(len(top5_unique_users) - len(all34_unique_users))

    trace_all34 = go.Bar(
        x=departments,
        y=y0,
        name='全資質オープン済'
    )

    trace_top5 = go.Bar(
        x=departments,
        y=y1,
        name='TOP5のみ'
    )

    data = [trace_all34, trace_top5]

    return data


unique_users = set(df_top5.index)
header_contents = html.Div(
    [
        html.H5('診断済み社員数：{}名'.format(len(unique_users)),
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.Br()
    ]
)

title_contents = html.Div(
    [
        html.H5('資質ランキング',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")
                ),
        html.Br()
    ]
)

# 部署別の登録ユーザー数のグラフオブジェクトを作成
graph_registered_user_cnt_data = create_graph_registered_user_cnt(df_top5, df_all34)

graph_registered_user_cnt_each_division = html.Div(
    dcc.Graph(
        id='cnt',
        figure={
            'data': graph_registered_user_cnt_data,
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
    # 各資質の順位合計のグラフオブジェクトを作成
    graph_data = create_graph_strengths_rank_sum(
        rank_sum_each_departments,
        dict_colors_strengths,
        department
    )

    graph_rank_sum_each_department = html.Div(
        dcc.Graph(
            id='score_summary{}'.format(i+1),
            figure={
                'data': graph_data,
                'layout': {
                    'title': '資質の合計スコア({})'.format(department)
                }
            }
        ),
        style={'display': 'inline-block'})

    layout.append(graph_rank_sum_each_department)
