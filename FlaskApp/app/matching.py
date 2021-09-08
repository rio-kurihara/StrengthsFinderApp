import numpy as np
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from markdown_txt import txt as markdown_txt
from app.utils import nav_menu, create_content_header
import random
import pandas as pd

from pandas import DataFrame
import numpy as np


def get_layout(df_top5):
    layout = html.Div([
        nav_menu,
        create_content_header('マッチング',
                              '2つの入力ボックスに対象の方の氏名を入力してください'),
        html.P('メンティー集合を入力してください'),
        dcc.Dropdown(
            id='group_personsA',
            options=[{'label': i, 'value': i}
                     for i in np.unique(df_top5.index)],
            multi=True,
            style=dict(backgroundColor='#FFE4E1',
                       #    marginLeft='10px',
                       #   width='60%',
                       #    backgroundPaddingLeft="50px",
                       )
        ),
        html.Br(),
        html.P('メンター集合を入力してください'),
        dcc.Dropdown(
            id='group_personsB',
            options=[{'label': i, 'value': i}
                     for i in np.unique(df_top5.index)],
            multi=True,
            style=dict(backgroundColor='#E6E6FA',
                       #    marginLeft='10px',
                       #    width='60%',
                       #    paddingLeft="30px",
                       )
        ),
        html.Br(),
        html.B(id='matching_check',
                  style=dict(color='red')
               ),
        dcc.Graph(id='matching',
                  responsive=True,
                  )
    ], style=dict(margin="50px"))
    # style={'display': 'inline-block', }
    return layout




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
    return dict(
        syain=dict(
            str_num=syain,      # 社員名: id
            num_str=syain_swap  # id: 社員名
        ),
        strength=dict(
            str_num=strength,   # ストレングス: id
            num_str=strength_swap  # id: ストレングス
        )
    )



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
    print(female_keep_set, male_keep_set)
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
                    # print(female_keep_set)
                    # print(male_keep_set)
                else:
                    set_A[male].pop(0)  # 振られたら告白候補から取り除く

        is_all_keeped = True
        for male in set_A.keys():  # 探索終了条件 すべての男がキープ状態または告白候補がいない状態になったら終了
            if (male_keep_set[male] == "") and (not len(set_A[male]) == 0):
                is_all_keeped = False
        if is_all_keeped:
            break
    return female_keep_set
    # print(female_keep_set)
