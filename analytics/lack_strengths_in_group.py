import json
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP


def aggregate(df):
    # 各資質の平均と最小値集計
    df_mean = df.groupby('strengths').mean()
    sr_mean = df_mean['rank'].map(lambda x: int(
        Decimal(str(x)).quantize(Decimal('0'), rounding=ROUND_HALF_UP)))

    df_min = df.groupby('strengths').min()

    df_aggregate = pd.concat([sr_mean, df_min], axis=1)
    df_aggregate.columns = ['mean', 'min']
    return df_aggregate


def main(df_org, target_names, topN, output_num):
    # データ抽出
    df = df_org.loc[target_names]

    # 各資質の平均と最小値集計
    df_aggregate = aggregate(df)

    # 最小値がN位以内の資質を削除
    df_under = df_aggregate[df_aggregate['min'] > topN].sort_values('mean')[
        ::-1]

    # 平均が高い上位2つの資質を抽出
    df_weakly = df_under.head(output_num)
    dict_weakly_info = df_weakly.reset_index().to_dict(orient='list')

    return dict_weakly_info


def list2markdown(list_message):
    """
    資質の説明message(リスト形式)をマークダウンに変換
    """
    list_message = ['・' + x for x in list_message]
    str_message = '  \n '.join(list_message)
    return str_message


def create_maerkdown_text(dict_strengths_message, dict_lack_result, index_num):
    strengths_name = dict_lack_result['strengths'][index_num]
    list_message = dict_strengths_message[strengths_name]['長所']
    strengths_message = list2markdown(list_message)
    strengths_mean = dict_lack_result['mean'][index_num]
    strengths_min = dict_lack_result['min'][index_num]

    text = """
    #### {0}
    
    {1}  
    ***
    このグループ内の{0}の平均順位は**{2}位**、  
    最高順位は**{3}位**です。

    """.format(strengths_name, strengths_message, strengths_mean, strengths_min)
    return text


# if __name__ == "__main__":
#     # set params
#     path = '../data/all34_exists_null.csv'
#     message_path = '../data/strengths_message.json'
#     topN = 10  # topN位以上の資質が含まれていれば足りない資質ではないとする
#     output_num = 2  # 最大でいくつの資質を出力するか
#     target_names = ['氏名1', '氏名2', ...]

#     # load strengths data
#     df_org = pd.read_csv(path, index_col='index')

#     # load message data
#     with open(message_path, 'r') as r:
#         dict_message = json.load(r)

#     dict_weakly_info = main(df_org, target_names, topN, output_num)
#     print_output(dict_weakly_info)  # 組み込み時不要．参考関数
