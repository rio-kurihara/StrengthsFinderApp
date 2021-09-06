import pandas as pd
import numpy as np

import os
import sys

from decimal import Decimal, ROUND_HALF_UP


def read_csv(path):
    df = pd.read_csv(path)
    return df


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

    # df = read_csv("../data/member_strengths.csv")
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


# if __name__ == "__main__":
#     main()
