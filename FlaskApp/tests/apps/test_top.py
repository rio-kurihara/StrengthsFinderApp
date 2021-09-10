import pickle

import pandas as pd
import plotly

from src.apps.top import create_strengths_rank_list


def test_create_strengths_rank_list():
    # sample data
    df = pd.read_csv('../tests/sample_data/sample_all34_exists_null.csv', index_col='index')
    with open("../tests/sample_data/mst/dict_colors_strengths.pkl", mode='rb') as f:
        dict_colors_strengths = pickle.load(f)
    with open("../tests/sample_data/mst/dict_strengths_desc.pkl", mode='rb') as f:
        dict_strengths_desc = pickle.load(f)
    list_person = ['04TC6RBN']

    data = create_strengths_rank_list(df, dict_colors_strengths, dict_strengths_desc, list_person)

    expected_data_type = list
    expected_data_len = 34
    expected_element_type = plotly.graph_objs._bar.Bar

    assert isinstance(data, expected_data_type)
    assert len(data) == expected_data_len
    assert isinstance(data[0], expected_element_type)
