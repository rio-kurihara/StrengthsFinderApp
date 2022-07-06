import pickle

import pandas as pd
import plotly

from FlaskApp.src.apps.list import create_strengths_rank_list


def test_create_strengths_rank_list():
    # サンプルデータの読み込み
    df = pd.read_csv('tests/sample_data/preprocessed/all34_sample.csv', index_col='user_name')
    with open("tests/sample_data/mst/dict_colors_strengths.pkl", mode='rb') as f:
        dict_colors_strengths = pickle.load(f)
    with open("tests/sample_data/mst/dict_strengths_desc.pkl", mode='rb') as f:
        dict_strengths_desc = pickle.load(f)
    # ユーザーからの入力データ例
    list_person = ['2S5OY2TI']

    # グラフオブジェクトを作成
    actual = create_strengths_rank_list(df, dict_colors_strengths, dict_strengths_desc, list_person)

    # 期待される型など
    expected_data_type = list
    expected_data_len = 34
    expected_element_type = plotly.graph_objs._bar.Bar

    # 結果が list かどうか確認
    assert isinstance(actual, expected_data_type)
    # 結果が全資質の34個分あるかどうか確認
    assert len(actual) == expected_data_len
    # 結果のリストの中身が plotly のグラフオブジェクトか確認
    assert isinstance(actual[0], expected_element_type)
