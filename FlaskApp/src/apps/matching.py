import random

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import yaml
from dash import dcc, html
from dash.dependencies import Input, Output
from pandas import DataFrame

from app import app


def ask(male, female_wish, keeped_male):
    # 告白に成功したらTrueを返す
    if keeped_male == "":       # キープがいない場合
        return True
    elif female_wish.index(male) < female_wish.index(keeped_male):
        # キープしている相手より優先順位が高い場合
        return True
    else:
        return False


def make_dict(df: DataFrame) -> dict:
    """社員ノードと特徴量の変換辞書を作成する
    Parameters
    ----------
    df : pd.DataFrame
        今回の分析対象csvをread_csvしたdf
        ```
        >>> df.columns
        Index(['rank', '氏名1', '氏名2', ...])
        ```
    Returns
    -------
    dict
        社員名とストレングスのidとの対応辞書
    """
    syain = {k: num for num, k in enumerate(df.columns[1:])}
    syain_swap = {v: k for k, v in syain.items()}
    strength_set = set(df[syain.keys()][:5].values.flatten())
    strength = {k: num for num, k in enumerate(strength_set)}
    strength_swap = {v: k for k, v in strength.items()}

    result = dict(
        syain=dict(
            str_num=syain,      # 社員名: id
            num_str=syain_swap  # id: 社員名
        ),
        strength=dict(
            str_num=strength,   # ストレングス: id
            num_str=strength_swap  # id: ストレングス
        )
    )

    return result


def prefer_order(list_A: list, list_B: list, num_dict: dict, res_mat: np.array) -> tuple:
    """cos類似度行列から希望順をピックアップさせる
    """
    list_A_num = [num_dict['syain']['str_num'][name] for name in list_A]
    list_B_num = [num_dict['syain']['str_num'][name] for name in list_B]
    order_A_val = res_mat[list_A_num][:, list_B_num]  # list_Aから見たlist_Bのcos数値
    order_B_val = res_mat[list_B_num][:, list_A_num]  # list_Bから見たlist_Aのcos数値
    # srder_A_valの値に従い高い順にlist_Bを並べ替える
    order_A_name = np.array(list_B)[np.argsort(order_A_val)[:, ::-1]]
    # srder_B_valの値に従い高い順にlist_Aを並べ替える
    order_B_name = np.array(list_A)[np.argsort(order_B_val)[:, ::-1]]
    set_A = {a: list(ob) for a, ob in zip(list_A, order_A_name)}
    set_B = {b: list(oa) for b, oa in zip(list_B, order_B_name)}
    return (set_A, set_B)


def search_stable_matching(set_A, set_B):
    # set_A と set_B の安定マッチングを探索する.
    # set_A に有利なマッチングを行う
    female_keep_set = {}
    male_keep_set = {}

    # 初期化
    for female in set_B.keys():
        female_keep_set[female] = ""
    for male in set_A.keys():
        male_keep_set[male] = ""
    # print(female_keep_set, male_keep_set)
    # 告白順は関係ないため、シャッフルを適用
    ask_order_list = random.sample(set_A.keys(), len(set_A.keys()))
    is_all_keeped = False

    while not is_all_keeped:
        for male in ask_order_list:
            # キープできていない且つ告白候補が存在する場合
            if male_keep_set[male] == "" and not len(set_A[male]) == 0:
                female = set_A[male][0]
                # print(male, female, set_B[female], female_keep_set[female])
                if ask(male, set_B[female], female_keep_set[female]):  # 告白が成功した場合
                    tmp_keep_male = female_keep_set[female]  # 告白によりキープされなくなった
                    tmp_keep_female = male_keep_set[male]
                    if not tmp_keep_male == "":  # キープからフリーになった
                        male_keep_set[male] = female
                        male_keep_set[tmp_keep_male] = ""
                        set_A[male].pop(0)
                    else:
                        male_keep_set[male] = female

                    if not tmp_keep_female == "":  # キープからフリーになった
                        female_keep_set[female] = male
                        female_keep_set[tmp_keep_female] = ""
                    else:
                        female_keep_set[female] = male
                else:
                    set_A[male].pop(0)  # 振られたら告白候補から取り除く

        is_all_keeped = True
        for male in set_A.keys():  # 探索終了条件 すべての男がキープ状態または告白候補がいない状態になったら終了
            if (male_keep_set[male] == "") and (not len(set_A[male]) == 0):
                is_all_keeped = False
        if is_all_keeped:
            break
    return female_keep_set


# settings
with open('settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)
strengths_path = config['base_dir'] + config['strengths_path']
top5_path = config['base_dir'] + config['top5_path']

# load data
df_top5 = pd.read_csv(top5_path, index_col='user_name')
df_strength = pd.read_csv(strengths_path)


header_contents = html.Div(
    [
        html.H5('マッチング',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P('2つの入力ボックスに対象の方の氏名を入力してください')
    ]
)

groupA_drop_down_list = dcc.Dropdown(
    id='group_usersA',
    options=[{'label': i, 'value': i}
             for i in np.unique(df_top5.index)],
    multi=True,
    style=dict(backgroundColor='#FFE4E1',
               #    marginLeft='10px',
               #   width='60%',
               #    backgroundPaddingLeft="50px",
               )
)

groupB_drop_down_list = dcc.Dropdown(
    id='group_usersB',
    options=[{'label': i, 'value': i}
             for i in np.unique(df_top5.index)],
    multi=True,
    style=dict(backgroundColor='#E6E6FA',
               #    marginLeft='10px',
               #    width='60%',
               #    paddingLeft="30px",
               )
)

layout = html.Div(
    [
        header_contents,
        html.P('メンティー集合を入力してください'),
        groupA_drop_down_list,

        html.Br(),

        html.P('メンター集合を入力してください'),
        groupB_drop_down_list,

        html.Br(),

        html.B(id='matching_check',
               style=dict(color='red')
               ),
        dcc.Graph(id='matching_result',
                  responsive=True,
                  )
    ]
)


@app.callback(Output('matching_check', 'children'),
              [Input('group_usersA', 'value'),
               Input('group_usersB', 'value')])
def check_matching_input(list_userA, list_userB):
    if len(set(list_userA) & set(list_userB)) != 0:
        return 'メンティー集合とメンター集合に重複があります'
    elif len(set(list_userA)) > len(set(list_userB)):
        return 'メンティー集合の要素をメンター集合の要素と同等以下になるように減らしてください'
    else:
        return True


@app.callback(Output('matching_result', 'figure'),
              [Input('matching_check', 'children'),
               Input('group_usersA', 'value'),
               Input('group_usersB', 'value')])
def update_matching(check_result, list_userA, list_userB):
    try:
        del result
        print('delete result')
    except:
        pass

    if check_result == False:
        return {'data': None, 'layout': None}
    else:
        num_dict = make_dict(df_strength)
        res_cos_path = config['base_dir'] + config['res_cos_name_path']
        res_mat = np.array(pd.read_csv(res_cos_path))
        set_A, set_B = prefer_order(
            list_userA, list_userB, num_dict, res_mat)
        result = search_stable_matching(set_A, set_B)
        df_result = pd.DataFrame.from_dict(
            result, orient='index').reset_index()
        df_result.columns = ['メンター', 'メンティー']
        df_result = df_result[['メンティー', 'メンター']]
        df_result = df_result[df_result['メンティー'] != '']

        data = [go.Table(
                header=dict(values=df_result.columns,
                            align='center',
                            line=dict(color='darkslategray'),
                            fill=dict(color=['#FFE4E1', '#E6E6FA'],)
                            ),
                cells=dict(values=df_result.values.T,
                           align='center',
                           line=dict(color='darkslategray'),
                           font=dict(color='darkslategray'),
                           fill=dict(color='white'),
                           ),
                )]

        layout = go.Layout(
            title='マッチング結果',
            font=dict(size=15),
            hovermode='closest',
            # height=1800,
            # width=2500,
            barmode='stack',
            showlegend=False,
            xaxis=dict(title="Strengths",
                       side='top',
                       tickangle=90),
            yaxis=dict(autorange='reversed',
                       showgrid=False,
                       zeroline=False,
                       showline=False,
                       ticks='',
                       dtick=1
                       )
        )

        return {'data': data, 'layout': layout}
