import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
from src.create_data_for_app import convert_vertical


def convert_vertical():
    sample_data_path = '../tests/sample_data/original/strengths_sample.csv'
    df = pd.read_csv(sample_data_path, index_col='rank').T

    actual = convert_vertical(df)

    expected = pd.DataFrame(
        data={
            'user_name': ['2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP', '2S5OY2TI', '3TT9OJOP'],
            'strengths': ['個別化', '原点思考', '回復志向', '適応性', '自我', '収集心', 'コミュニケーション', '学習欲', '調和性', '内省', '収集心', np.nan, '慎重さ', np.nan, '信念', np.nan, '内省', np.nan, '分析思考', np.nan, '適応性', np.nan, 'アレンジ', np.nan, '目標志向', np.nan, '着想', np.nan, '戦略性', np.nan, 'ポジティブ', np.nan, '成長促進', np.nan, '学習欲', np.nan, '規律性', np.nan, '活発性', np.nan, '運命思考', np.nan, '親密性', np.nan, '責任感', np.nan, '社交性', np.nan, '共感性', np.nan, '包含', np.nan, '最上志向', np.nan, '未来志向', np.nan, '自己確信', np.nan, '指令性', np.nan, '達成欲', np.nan, '競争性', np.nan, '公平性', np.nan, '原点思考', np.nan],
            'rank': [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 23, 24, 24, 25, 25, 26, 26, 27, 27, 28, 28, 29, 29, 30, 30, 31, 31, 32, 32, 33, 33, 34, 34]
        }
    )

    assert_frame_equal(actual, expected)
