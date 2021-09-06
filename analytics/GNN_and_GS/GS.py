import random

from attrdict import AttrDict
from pandas import DataFrame
import numpy as np
import pandas as pd
import yaml

# set_A = {"A": ["c", "a", "b"], "B": ["c", "b", "a"], "C": ["a", "c", "b"], "D": ["a", "c", "b"], "E": ["c", "b", "a"]}
# set_B = {"a": ["A", "D", "B", "E", "C"], "b": ["C", "A", "D", "E", "B"], "c": ["E", "C", "B", "A", "D"]}


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


def load_config(config_path: str) -> AttrDict:
    """config(yaml)ファイルを読み込む

    Parameters
    ----------
    config_path : string
        config fileのパスを指定する

    Returns
    -------
    config : attrdict.AttrDict
        configを読み込んでattrdictにしたもの
    """
    with open(config_path, 'r', encoding='utf-8') as fi_:
        return AttrDict(yaml.load(fi_, Loader=yaml.SafeLoader))


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


def ask(male, female_wish, keeped_male):
    # 告白に成功したらTrueを返す
    if keeped_male == "":       # キープがいない場合
        return True
    elif female_wish.index(male) < female_wish.index(keeped_male):
        # キープしている相手より優先順位が高い場合
        return True
    else:
        return False


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


# if __name__ == "__main__":
#     conf = load_config('./GNN_and_GS/config.yaml')

#     df = pd.read_csv('../data/member_strengths.csv')
#     num_dict = make_dict(df)
#     res_mat = np.loadtxt(conf.save_res_cos_name, delimiter=',')
#     # 画面で下記のリストを受け取る形にする
#     # 新卒
#     list_A = ['氏名1', '氏名2', ...]
#     # 1on1相手候補
#     list_B = ['氏名1', '氏名2', ...]
#     set_A, set_B = prefer_order(list_A, list_B, num_dict, res_mat)
#     if len(set_A) <= len(set_B):  # もうちょい発動条件を厳しくしても良いが、一旦簡単に。
#         search_stable_matching(set_A, set_B)
#     else:
#         print('1on1相手候補が足りません。')
