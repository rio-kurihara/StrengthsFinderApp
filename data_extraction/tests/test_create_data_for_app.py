from unittest import expectedFailure
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
from src.create_data_for_app import convert_vertical, check_top5_null, split_top5_and_all34


def convert_vertical():
    # 横持ちのデータセットを読み込む
    """ exsample
    |rank|user_name_1|user_name_2|
    |---|---|---|
    |1|strengths_A|strengths_B|
    |2|strengths_C|strengths_D|
    |...|...|...|
    """
    sample_data_path = '../tests/sample_data/original/strengths_sample.csv'
    df = pd.read_csv(sample_data_path, index_col='rank').T

    # 縦持ちに変換する
    """ exsample
    |user_name|strengths|rank|
    |---|---|---|
    |user_name_1|strengths_A|1|
    |user_name_2|strengths_B|1|
    |user_name_1|strengths_C|2|
    |...|...|...|
    """
    expected = pd.DataFrame(
        data={
            'user_name': ['2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP'],
            'strengths': ['個別化', '原点思考', '回復志向', '適応性', '自我', '収集心', 'コミュニケーション', '学習欲', '調和性', '内省', '収集心', np.nan, '慎重さ', np.nan, '信念', np.nan, '内省', np.nan, '分析思考', np.nan, '適応性', np.nan, 'アレンジ', np.nan, '目標志向', np.nan, '着想', np.nan, '戦略性', np.nan, 'ポジティブ', np.nan, '成長促進', np.nan, '学習欲', np.nan, '規律性', np.nan, '活発性', np.nan, '運命思考', np.nan, '親密性', np.nan, '責任感', np.nan, '社交性', np.nan, '共感性', np.nan, '包含', np.nan, '最上志向', np.nan, '未来志向', np.nan, '自己確信', np.nan, '指令性', np.nan, '達成欲', np.nan, '競争性', np.nan, '公平性', np.nan, '原点思考', np.nan],
            'rank': [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 23, 24, 24, 25, 25, 26, 26, 27, 27, 28, 28, 29, 29, 30, 30, 31, 31, 32, 32, 33, 33, 34, 34]
        }
    )

    actual = convert_vertical(df)
    assert_frame_equal(actual, expected)


def test_check_top5_null():
    # テストデータを準備：上位5位以内に NULL が含まれる場合とそうでない場合 ※上位6位以降に NULL が含まれているのは後者に該当
    df_with_null = pd.DataFrame(
        data={
            'user_name': ['2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP'],
            'strengths': [np.nan, '原点思考', '回復志向', '適応性', '自我', '収集心', 'コミュニケーション', '学習欲', '調和性', '内省', '収集心', np.nan, '慎重さ', np.nan, '信念', np.nan, '内省', np.nan, '分析思考', np.nan, '適応性', np.nan, 'アレンジ', np.nan, '目標志向', np.nan, '着想', np.nan, '戦略性', np.nan, 'ポジティブ', np.nan, '成長促進', np.nan, '学習欲', np.nan, '規律性', np.nan, '活発性', np.nan, '運命思考', np.nan, '親密性', np.nan, '責任感', np.nan, '社交性', np.nan, '共感性', np.nan, '包含', np.nan, '最上志向', np.nan, '未来志向', np.nan, '自己確信', np.nan, '指令性', np.nan, '達成欲', np.nan, '競争性', np.nan, '公平性', np.nan, '原点思考', np.nan],
            'rank': [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 23, 24, 24, 25, 25, 26, 26, 27, 27, 28, 28, 29, 29, 30, 30, 31, 31, 32, 32, 33, 33, 34, 34]
        }
    )
    df_without_null = pd.DataFrame(
        data={
            'user_name': ['2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP'],
            'strengths': ['個別化', '原点思考', '回復志向', '適応性', '自我', '収集心', 'コミュニケーション', '学習欲', '調和性', '内省', '収集心', np.nan, '慎重さ', np.nan, '信念', np.nan, '内省', np.nan, '分析思考', np.nan, '適応性', np.nan, 'アレンジ', np.nan, '目標志向', np.nan, '着想', np.nan, '戦略性', np.nan, 'ポジティブ', np.nan, '成長促進', np.nan, '学習欲', np.nan, '規律性', np.nan, '活発性', np.nan, '運命思考', np.nan, '親密性', np.nan, '責任感', np.nan, '社交性', np.nan, '共感性', np.nan, '包含', np.nan, '最上志向', np.nan, '未来志向', np.nan, '自己確信', np.nan, '指令性', np.nan, '達成欲', np.nan, '競争性', np.nan, '公平性', np.nan, '原点思考', np.nan],
            'rank': [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 23, 24, 24, 25, 25, 26, 26, 27, 27, 28, 28, 29, 29, 30, 30, 31, 31, 32, 32, 33, 33, 34, 34]
        }
    )

    # NULL が含まれるデータの場合：NULL のユーザーのデータを全て消去して返す
    expected_with_null = pd.DataFrame(
        data={
            'user_name': ['3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP', '3TT9OJOP'],
            'strengths': ['原点思考', '適応性', '収集心', '学習欲', '内省', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            'rank': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34]
        }
    )
    actual_with_null = check_top5_null(df_with_null)
    assert_frame_equal(actual_with_null, expected_with_null)

    # NULL が含まれないデータの場合：入力データをそのまま返す
    actual_without_null = check_top5_null(df_without_null)
    assert_frame_equal(actual_without_null, df_without_null)


def test_split_top5_and_all34():
    # 入力データのサンプルを作成
    """ exsample
    |                       |strengths|rank|department|
    |(index_name: user_name)|---|---|---|
    |user_name_1            |strengths_A|1|XXX|
    |user_name_2            |strengths_B|1|YYY|
    |...|...|...|...|
    """
    df_input = pd.DataFrame(
        index=['2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP',
               '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP',
               '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP',
               '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP',
               '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP',
               '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP',
               '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP',
               '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP',
               '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP',
               '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP',
               '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP',
               '2S5OY2TI', '3TT9OJOP'],
        data={
            'strengths': ['個別化', '原点思考', '回復志向', '適応性', '自我', '収集心', 'コミュニケーション', '学習欲', '調和性', '内省', '収集心', np.nan, '慎重さ', np.nan, '信念', np.nan, '内省', np.nan, '分析思考', np.nan, '適応性', np.nan, 'アレンジ', np.nan, '目標志向', np.nan, '着想', np.nan, '戦略性', np.nan, 'ポジティブ', np.nan, '成長促進', np.nan, '学習欲', np.nan, '規律性', np.nan, '活発性', np.nan, '運命思考', np.nan, '親密性', np.nan, '責任感', np.nan, '社交性', np.nan, '共感性', np.nan, '包含', np.nan, '最上志向', np.nan, '未来志向', np.nan, '自己確信', np.nan, '指令性', np.nan, '達成欲', np.nan, '競争性', np.nan, '公平性', np.nan, '原点思考', np.nan],
            'rank': [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 23, 24, 24, 25, 25, 26, 26, 27, 27, 28, 28, 29, 29, 30, 30, 31, 31, 32, 32, 33, 33, 34, 34],
            'department': ['XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY']
        }
    )
    df_input.index.name = 'user_name'

    # 期待されるデータ：上位5位のみのデータ
    expected_top5 = pd.DataFrame(
        data={
            'user_name': ['2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP'],
            'strengths': ['個別化', '原点思考', '回復志向', '適応性', '自我', '収集心', 'コミュニケーション', '学習欲', '調和性', '内省'],
            'rank': [1, 1, 2, 2, 3, 3, 4, 4, 5, 5],
            'department': ['XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY', 'XXX', 'YYY']
        }
    )

    # 期待されるデータ：34位までの全てのデータ
    expected_all = pd.DataFrame(
        data={
            'user_name': ['2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI', '2S5OY2TI'],
            'strengths': ['個別化', '回復志向', '自我', 'コミュニケーション', '調和性', '収集心', '慎重さ', '信念', '内省', '分析思考', '適応性', 'アレンジ', '目標志向', '着想', '戦略性', 'ポジティブ', '成長促進', '学習欲', '規律性', '活発性', '運命思考', '親密性', '責任感', '社交性', '共感性', '包含', '最上志向', '未来志向', '自己確信', '指令性', '達成欲', '競争性', '公平性', '原点思考'],
            'rank': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34],
            'department': ['XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX', 'XXX']
        }
    )

    actual_top5, actual_all = split_top5_and_all34(df_input)

    assert_frame_equal(actual_top5, expected_top5)
    assert_frame_equal(actual_all, expected_all)
