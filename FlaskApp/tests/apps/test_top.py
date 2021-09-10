import plotly
# import pickle

# import dash_core_components as dcc
# import dash_html_components as html
# import numpy as np
# import pandas as pd
# import plotly.graph_objs as go
# import yaml
# from dash.dependencies import Input, Output


from apps.top import create_strengths_rank_list

import pandas as pd

# path = "../data/preprocessed/all34_exists_null.csv"
# df = pd.read_csv(path)
# print(df[df['index'] in ['4FH202RH', '2S5OY2TI']])


# def create_strengths_rank_list(df, dict_colors_strengths, dict_strengths_desc, list_person):
#     """ユーザーの資質一覧を表示するためのグラフオブジェクトを作成

#     Args:
#         df (pd.DataFrame): 全ユーザーの資質ランキング
#         dict_colors_strengths (dict): 各資質のカラーコード
#                                     ex: {'責任感': '#ffbcdd', '達成欲': '#ffbcdd', ...}
#         dict_strengths_desc (dict): 各資質の説明
#                                     ex: {'収集心': '収集や蓄積を必要とします',
#                                         '分析思考': '物事の理由と原因を追究します',
#                                         ...}
#         list_person (list): 任意のユーザー名のリスト

#     Returns:
#         list: グラフオブジェクトのリスト
#     """

#     data = []
#     num_strengths = 35

#     for i_th in range(1, num_strengths):

#         i_th_strenghts = list(df[df['rank'] == i_th].loc[list_person]['strengths'])
#         colors_for_strenghts = [dict_colors_strengths[_x] for _x in i_th_strenghts]

#         marker = dict(
#             color=colors_for_strenghts,
#             line=dict(color='rgb(8,48,107)', width=1.5)
#         )

#         description_for_strengths = [dict_strengths_desc[_x] for _x in i_th_strenghts]
#         i_th_strenghts_for_display = [_x.replace(_x, 'コミュニ<br>ケ―ション')
#                                       if _x == 'コミュニケーション' else _x for _x in i_th_strenghts]

#         trace = go.Bar(
#             x=list_person,
#             y=[1] * len(list_person),
#             marker=marker,
#             hoverinfo='text',
#             hovertext=description_for_strengths,
#             text=i_th_strenghts_for_display,
#             textposition='inside'
#         )

#         data.append(trace)

#     return data


# df = pd.read_csv('../sample_data/sample_all34_exists_null.csv', index_col='index')
# with open("../sample_data/mst/dict_colors_strengths.pkl", mode='rb') as f:
#     dict_colors_strengths = pickle.load(f)
# with open("../sample_data/mst/dict_strengths_desc.pkl", mode='rb') as f:
#     dict_strengths_desc = pickle.load(f)
# list_person = ['04TC6RBN']


# a = create_strengths_rank_list(df, dict_colors_strengths, dict_strengths_desc, list_person)

# print(type(a))
# print(len(a))
# print(type(a[0]))
# print(a[0])


def test_create_strengths_rank_list():
    # sample data
    df = pd.read_csv('../sample_data/sample_all34_exists_null.csv', index_col='index')
    with open("../sample_data/mst/dict_colors_strengths.pkl", mode='rb') as f:
        dict_colors_strengths = pickle.load(f)
    with open("../sample_data/mst/dict_strengths_desc.pkl", mode='rb') as f:
        dict_strengths_desc = pickle.load(f)
    list_person = ['04TC6RBN']

    data = create_strengths_rank_list(df, dict_colors_strengths, dict_strengths_desc, list_person)

    expected_data_len = 34

    assert isinstance(data, list)
    assert len(data) == expected_data_len
    assert isinstance(data[0], plotly.graph_objs._bar.Bar)
    # assert data[0] == plotly.graph_objs._bar.Bar(
    #     {
    #         'hoverinfo': 'text',
    #         'hovertext': [アイデアを実行に移すことにより結果をもたらします。< br > 単に話すだけではなく、いますぐ実行することを望みます。],
    #         'marker': {'color': ['#ffffad'], 'line': {'color': 'rgb(8,48,107)', 'width': 1.5}},
    #         'text': [活発性],
    #         'textposition': 'inside',
    #         'x': [04TC6RBN],
    #         'y': [1]
    #     }
    # )
