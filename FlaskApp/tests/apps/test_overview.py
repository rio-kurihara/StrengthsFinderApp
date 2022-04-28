import pandas as pd
from src.apps.overview import (create_graph_registered_user_cnt,
                               create_graph_strengths_rank_sum)


def test_create_graph_registered_user_cnt():
    # sample data
    df_top5 = pd.read_csv('tests/sample_data/preprocessed/top5_sample.csv', index_col='user_name')
    df_all34 = pd.read_csv('tests/sample_data/preprocessed/all34_sample.csv', index_col='user_name')

    res = create_graph_registered_user_cnt(df_top5, df_all34)
    print(res)
