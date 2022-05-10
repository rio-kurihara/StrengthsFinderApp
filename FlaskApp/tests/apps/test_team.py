import numpy as np
import json

import pandas as pd
from pandas.testing import assert_frame_equal
from numpy import extract
from src.apps.team import (calc_mean_and_min, create_display_text_for_lack,
                           lack_strengths_in_team, list_to_bullets_str,
                           sum_rank_each_strengths_category, extract_unique_strength,
                           create_display_text_for_unique, calc_rank_diff, extract_unique_strength)


def test_sum_rank_each_strengths_category():
    # サンプルデータの読み込み
    path = 'tests/sample_data/preprocessed/top5_sample.csv'
    df_top5 = pd.read_csv(path, index_col='user_name')
    # 各資質のカテゴリ定義
    with open('tests/sample_data/mst/dict_strengths_category.json') as f:
        dict_strengths_category = json.load(f)

    # データフレームにカテゴリ列を追加
    df_top5['category'] = df_top5[['strengths']
                                  ].applymap(dict_strengths_category.get)
    # サンプルユーザーの設定
    user = '2S5OY2TI'

    # カテゴリ別の順位の合計結果
    expected = {'人間関係構築力': 6, '実行力': 4, '影響力': 5}

    actual = sum_rank_each_strengths_category(df_top5, user)

    assert actual == expected


def test_list_to_bullets_str():
    # サンプルのインプット：資質の説明文のリスト
    sample_input = ['複数の物、人を組み合わせて効率的に進める', '1つのやり方にとらわれず柔軟に進める', '自分は主役にならずに指揮を振る']
    # リストの要素をそれぞれ箇条書きにし、文字列として連結する
    actual = list_to_bullets_str(sample_input)

    expected = '・複数の物、人を組み合わせて効率的に進める  \n ・1つのやり方にとらわれず柔軟に進める  \n ・自分は主役にならずに指揮を振る'

    assert actual == expected


def test_create_display_text_for_lack():
    # サンプルデータの準備
    dict_strengths_message = pd.read_json('tests/sample_data/mst/strengths_message.json')
    # 任意のグループ内で不足している資質とその平均順位と最低順位
    dict_lack_result = {'strengths': ['公平性', '慎重さ'], 'mean': [34, 35], 'min': [34, 33]}

    expected_1 = """
    #### 公平性
    
    ・手順に従い同じ方法で淡々と物事を実行することができる  
 ・みんなが納得できるルールを作ることができる  
 ・えこひいきをせず言行一致しているので、透明性が高く周囲の人から信頼される  
    ***
    このグループ内の 公平性 の平均順位は**34位**、  
    最高順位は**34位**です。
    """

    expected_2 = """
    #### 慎重さ
    
    ・リスクを予見して避けることができ、無駄な時間を使わずに済む  
 ・じっくりと時間をかけて検討することができる  
 ・不安から十分な期間を取って物事に取り組む  
    ***
    このグループ内の 慎重さ の平均順位は**35位**、  
    最高順位は**33位**です。
    """

    actual_1 = create_display_text_for_lack(dict_strengths_message, dict_lack_result, 0)
    actual_2 = create_display_text_for_lack(dict_strengths_message, dict_lack_result, 1)

    assert actual_1 == expected_1
    assert actual_2 == expected_2


def test_calc_mean_and_min():
    # サンプルデータの読み込み
    path = 'tests/sample_data/preprocessed/all34_exists_null_sample.csv'
    df_all = pd.read_csv(path, index_col='user_name')
    # 特定のユーザーを対象に集計
    target_users = ['2S5OY2TI', '3TT9OJOP']
    df = df_all.loc[target_users]

    # 資質別の平均順位と最低順位を集計
    expected = pd.DataFrame(
        data={
            'mean': [12, 4, 16, 8, 1, 33, 25, 7, 10, 26, 18, 5, 2, 11, 7, 17, 15, 30, 27, 28, 20, 13, 14, 24, 32, 29, 3, 19, 22, 5, 23, 21, 31, 7],
            'min': [12, 4, 16, 8, 1, 33, 25, 5, 10, 26, 1, 3, 2, 4, 7, 17, 15, 30, 27, 28, 20, 13, 14, 24, 32, 29, 3, 19, 22, 5, 23, 21, 31, 2],
        }
    )
    expected.index = ['アレンジ', 'コミュニケーション', 'ポジティブ', '信念', '個別化', '公平性', '共感性', '内省', '分析思考', '包含', '原点思考', '収集心', '回復志向', '学習欲', '慎重さ',
                      '成長促進', '戦略性', '指令性', '最上志向', '未来志向', '活発性', '目標志向', '着想', '社交性', '競争性', '自己確信', '自我', '規律性', '親密性', '調和性', '責任感', '運命思考', '達成欲', '適応性']
    expected.index.name = 'strengths'

    actual = calc_mean_and_min(df)

    assert_frame_equal(actual, expected)


def test_lack_strengths_in_team():
    # サンプルデータの読み込み
    path = 'tests/sample_data/preprocessed/all34_exists_null_sample.csv'
    df_all = pd.read_csv(path, index_col='user_name')
    # 集計対象のユーザーを指定
    list_users = ['2S5OY2TI', '3TT9OJOP']

    # 指定したユーザー内において、平均順位が低く、かつ10位以上の資質が含まれない資質を二つ出力する
    expected_1 = {'strengths': ['公平性', '競争性'], 'mean': [33, 32], 'min': [33, 32]}
    actual_1 = lack_strengths_in_team(df_org=df_all,
                                      target_users=list_users,
                                      topN=10,
                                      output_num=2)
    assert actual_1 == expected_1

    # 指定したユーザー内において、平均順位が低く、かつ15位以上の資質が含まれない資質を三つ出力する
    expected_2 = {'strengths': ['公平性', '競争性', '達成欲'], 'mean': [33, 32, 31], 'min': [33, 32, 31]}
    actual_2 = lack_strengths_in_team(df_org=df_all,
                                      target_users=list_users,
                                      topN=15,
                                      output_num=3)
    assert actual_2 == expected_2


def test_calc_rank_diff():
    # サンプルデータの読み込み
    df = pd.read_csv('tests/sample_data/preprocessed/all34_sample.csv')
    # 集計対象グループのユーザーの設定
    list_users = ['2S5OY2TI', '04TC6RBN']
    # 着目したいユーザーの設定
    target_user = '2S5OY2TI'

    # 集計対象のグループメンバーのデータを抽出
    df_extracted_group = df[df['user_name'].isin(list_users)]
    # 行に資質、列にユーザーとなるようにピボットする
    df_extracted_group_pivot = df_extracted_group.pivot_table(
        index="strengths", columns="user_name", values="rank")

    excepted = pd.DataFrame(
        data={
            '04TC6RBN': [5, 19, -12, -3, 1, 1, -11, 9, 19, 1, -4, 3, 29, -11, 26, -4, -4, -9, -19, -22, -19, -3, 6, -2, -20, -5, 22, 0, -6, 23, -8, 5, -28, 21]
        }
    )
    excepted.index = ['アレンジ', 'コミュニケーション', 'ポジティブ', '信念', '個別化', '公平性', '共感性', '内省', '分析思考',
                      '包含', '原点思考', '収集心', '回復志向', '学習欲', '慎重さ', '成長促進', '戦略性', '指令性', '最上志向',
                      '未来志向', '活発性', '目標志向', '着想', '社交性', '競争性', '自己確信', '自我', '規律性', '親密性',
                      '調和性', '責任感', '運命思考', '達成欲', '適応性']

    actual = calc_rank_diff(df_extracted_group_pivot, list_users, target_user)

    assert_frame_equal(actual, excepted)


def test_extract_unique_strength():
    # サンプルデータの読み込み
    df = pd.read_csv('tests/sample_data/preprocessed/all34_sample.csv')
    # 集計対象グループのユーザーの設定
    list_users = ['2S5OY2TI', '04TC6RBN']
    # 着目したいユーザーの設定
    target_user = '2S5OY2TI'

    excepted = {'strengths': ['回復志向', '慎重さ'],
                'target_rank': [2, 7],
                'member_avg_rank': [31., 33.]}

    actual = extract_unique_strength(df, list_users, target_user, top_n=2)

    assert actual == excepted


def test_create_display_text_for_unique():
    # サンプルデータの読み込み、定義
    dict_strengths_message = pd.read_json('tests/sample_data/mst/strengths_message.json')
    dict_unique_strengths = {'strengths': ['回復志向', '慎重さ'],
                             'target_rank': [2, 7],
                             'member_avg_rank': [31., 33.]}
    index_num = 0
    target_user = '2S5OY2TI'

    excepted = """
    #### 回復志向
    
    ・問題の根本原因を見つけて解決する  
 ・困ってる人を助ける  
 ・真正面から問題と向き合える  
    ***
    このグループ内の 回復志向 の平均順位は**31位**、  
    2S5OY2TI さんの順位は**2位**です。
    """

    actual = create_display_text_for_unique(dict_strengths_message,
                                            dict_unique_strengths,
                                            index_num,
                                            target_user)
    assert actual == excepted
