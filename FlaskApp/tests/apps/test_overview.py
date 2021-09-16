import pandas as pd
from src.apps.overview import (create_graph_registered_user_cnt,
                               create_graph_strengths_rank_sum)


def test_create_graph_registered_user_cnt():
    # sample data
    df_top5 = pd.read_csv('../tests/sample_data/sample_top5.csv', index_col='index')
    df_all34 = pd.read_csv('../tests/sample_data/sample_all34.csv', index_col='index')

    res = create_graph_registered_user_cnt(df_top5, df_all34)
    print(res)
